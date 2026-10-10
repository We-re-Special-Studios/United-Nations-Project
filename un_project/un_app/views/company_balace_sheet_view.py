from django.shortcuts import render, get_object_or_404
from django.db.models import F, Value, Sum, DecimalField, Prefetch
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from ..models import Company, Denomination, Building, Item, ItemCount, ItemSection, LiquidAssetContainer, Liability, CompanyShareholder



def company_balance_sheet(request, company_abbreviation):
    # Get the company by its abbreviation
    company = get_object_or_404(Company, abbreviation=company_abbreviation)
    denominations = Denomination.objects.all()
    
    # Fetch all buildings owned by the company
    #buildings = Building.objects.filter(owner=company)
    
     # Fetch buildings where the company is a partial owner
    partial_buildings = Building.objects.filter(
        partialbuildingownership__partial_owner_abbreviation=company.abbreviation
    ).annotate(
        ownership=F('partialbuildingownership__percentage')
    ).distinct()

    # --------------------------------------------------
    # Liquid assets
    # --------------------------------------------------
    # Fetch and sort liquid asset containers by ordering
    liquid_containers = LiquidAssetContainer.objects.filter(company=company).order_by('ordering')
    liquid_asset_data = []

    # Loop through each container to retrieve LiquidCounts and calculate values
    for container in liquid_containers:
        container_total_in_diamonds = Decimal('0')
        container_counts = []

        # Calculate counts and diamond equivalents for each denomination
        for denomination in denominations:
            count_entry = container.liquidcount_set.filter(denomination=denomination).first()
            count_value = count_entry.count if count_entry else Decimal('0')
            container_counts.append(count_value)

            # Calculate diamond equivalent for this denomination
            container_total_in_diamonds += count_value * denomination.diamond_equivalent

        liquid_asset_data.append({
            'container_name': container.name,
            'counts': container_counts,
            'total_in_diamonds': container_total_in_diamonds,
        })
        
    # --------------------------------------------------
    # Owned items grouped by ItemSection and table number
    # --------------------------------------------------
    # Fetch item counts for this company.
    items_with_count = ItemCount.objects.filter(company=company)

    item_count_dict = {
        item_count.item_id: (item_count.count, item_count.total_value)
        for item_count in items_with_count
    }

    # Create the five balance sheet tables and their sections.
    item_tables = {
        number: {
            "number": number,
            "sections": [],
        }
        for number in range(1, 6)
    }

    sections = (
        ItemSection.objects
        .prefetch_related(
            Prefetch(
                "items",
                queryset=Item.objects.order_by("ordering", "id"),
            )
        )
        .order_by("table_number", "ordering", "id")
    )

    assigned_item_ids = set()

    for section in sections:
        section_items = []

        for item in section.items.all():
            assigned_item_ids.add(item.id)

            count, total_value = item_count_dict.get(
                item.id, (0, Decimal("0"))
            )

            section_items.append({
                "name": item.name or "Unnamed Item",
                "market_value": item.market_value or Decimal("0"),
                "count": count,
                "total_value": total_value,
            })

        item_tables[section.table_number]["sections"].append({
            "name": section.name,
            "items": section_items,
        })

    # Keep items without a section visible rather than silently omitting them.
    unassigned_items = Item.objects.filter(section__isnull=True).order_by("ordering", "id")
    unassigned_data = []

    for item in unassigned_items:
        count, total_value = item_count_dict.get(
            item.id, (0, Decimal("0"))
        )

        unassigned_data.append({
            "name": item.name or "Unnamed Item",
            "market_value": item.market_value or Decimal("0"),
            "count": count,
            "total_value": total_value,
        })
        
    item_tables = list(item_tables.values())

    if unassigned_data:
        item_tables.append({
            "number": "Unassigned",
            "sections": [{
                "name": "Unassigned Items",
                "items": unassigned_data,
            }],
        })
    
    # --------------------------------------------------
    # Liabilities
    # --------------------------------------------------    
    # Fetch liabilities where this company is the debtor
    company_content_type = ContentType.objects.get_for_model(Company)
    liabilities = Liability.objects.filter(
        debtor_type=company_content_type,
        debtor_abbreviation=company_abbreviation
    ).order_by('liability_type', 'creditor_abbreviation')

    # Calculate liability totals
    total_liabilities = liabilities.aggregate(
        total=Sum('total_diamond_value'))['total'] or Decimal('0')
    total_remaining_liabilities = liabilities.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')
    
    # Fetch receivables (liabilities where this company is the creditor)
    receivables = Liability.objects.filter(
        creditor_type=company_content_type,
        creditor_abbreviation=company_abbreviation
    ).order_by('liability_type', 'debtor_abbreviation')

    # Calculate receivables totals
    total_receivables = receivables.aggregate(
        total=Sum('remaining_diamond_value'))['total'] or Decimal('0')

    # fetch stock investments
    company_content_type = ContentType.objects.get_for_model(Company)
    stock_investments = CompanyShareholder.objects.filter(
        shareholder_type=company_content_type,
        shareholder_abbreviation=company_abbreviation
    ).select_related('company')

    # Calculate total value of investments
    total_investment_value = Decimal('0')
    for investment in stock_investments:
        investment_company = investment.company
        
        # Get company's receivables
        company_receivables = Liability.objects.filter(
            creditor_type=company_content_type,
            creditor_abbreviation=investment_company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        # Get company's liabilities
        company_liabilities = Liability.objects.filter(
            debtor_type=company_content_type,
            debtor_abbreviation=investment_company.abbreviation
        ).aggregate(
            total=Coalesce(
                Sum('remaining_diamond_value'),
                Value(0, output_field=DecimalField(max_digits=20, decimal_places=6))
            )
        )['total']

        company_value = (
            investment_company.total_liquid_asset_value + 
            investment_company.total_item_asset_value + 
            investment_company.total_building_asset_value +
            company_receivables -
            company_liabilities
        )
        investment.value = (Decimal(str(investment.percentage)) * company_value) / Decimal('100')
        total_investment_value += investment.value
    
    # Calculate total assets
    total_assets = (
        company.total_liquid_asset_value + 
        company.total_item_asset_value + 
        company.total_building_asset_value +
        total_investment_value +
        total_receivables -
        total_remaining_liabilities
    )
    
    # Fetch shareholders and calculate their share values
    shareholders = company.shareholders.all()
    # Calculate share values manually instead of using annotation
    for shareholder in shareholders:
        shareholder.share_value = (Decimal(str(shareholder.percentage)) * total_assets) / Decimal('100')
        
    # Check if at least one shareholder has a board member
    show_board_members = any(shareholder.board_member for shareholder in shareholders)

            
    return render(request, 'company_balance_sheet.html', {
        'company': company,
        #'buildings': buildings,
        'headquarters': company.headquarters,
        'headquarters_unit': company.headquarters_unit,
        'shareholders': shareholders,
        'partial_buildings': partial_buildings,
        'item_tables': item_tables,
        'denominations': denominations,
        'liquid_asset_data': liquid_asset_data,
        'liabilities': liabilities,
        'total_liabilities': total_liabilities,
        'total_remaining_liabilities': total_remaining_liabilities,
        'receivables': receivables,
        'total_receivables': total_receivables,
        'stock_investments': stock_investments,
        'total_investment_value': total_investment_value,
        'total_assets': total_assets,
        'show_board_members': show_board_members,
    })