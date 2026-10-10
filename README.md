# **United Nations Official Records Website Project**
<img src="/un_project/un_app/static/images/un_seal.png" alt="UN Seal" width="350"/>

This project will eventually maybe become a replacement for our spreadsheets:

__Building Index:__
https://docs.google.com/spreadsheets/d/1UHE3NIoL8Cl78Vgs8Dlx_xnMDgdPvZiRhjuruxc6oF8/edit

__Finance Document:__
https://docs.google.com/spreadsheets/d/1JdZUSav9DEh1bBfTcVBIFID3sLobqyq5nqLV7MwNyWo/edit?gid=1449818067#gid=1449818067


## Setup
Setting up the repo is pretty easy:
First-time setup
1. Clone the repo
2. Create a Python virtual enviroment
3. Enter the virtual enviroment
4. Install Poetry
`pip install poetry`
5. Install dependancies using Poetry
`python poetry install`

Running the server locally:
6. Go to the folder: 
`cd un_project/`
7. In that folder set up the database by importing/creating all the data by running:
`python manage.py build_all`
8. Start the server and enjoy:
`python manage.py runserver`


## Todo Roadmap
<sup>*Bolded Items should be prioritized*</sup>
- **<ins>Balance Sheets</ins>**
    - [x] **Add Total Value of Total Cash & Cash Equivalents**
    - [x] **Add Total Value of buildings**
    - [x] Manually order liquid assets (maybe create asset model with ordering field like item)
    - [ ] Move item calculations to the database rather than when the page is loaded to speed up loading times
        - [x] Items: Total Value, Market Value
        - [x] Buildings: partial stuff
        - [x] Total Value of items, liquid, buildings
        - [ ] Liquid Assets: Per asset totals
        - [ ] Building heights
        - [ ] Nation average height & # of buildings
        - [ ] Territory average height & # of buildings
    - [x] **Create liability tables**
        - [x] Add Liability section
        - [x] Add Several different types of liabilities
        - [x] Add Total Liabilities
    - [x] **Create receivables & other assets tables**
        - [x] Add Receivables
        - [x] Add Stock Investments
    - [x] **Create total assets rundown**
        - [x] (Total Cash & Cash Equivalents, Total Items, Total Territories, Other Assets & Liabilities = Total Assets)
    - [ ] Create loan tables for companies
        - [ ] Mortgages, loans, and add Total Debt Assets
    - [x] **Create shareholders table for companies (Shareholder, %, diamond equivalent [total assets * %])**
- **<ins>Evaluation Pages</ins>**
    - [X] Must be logged in to see evaluation pages
    - [ ] **Be able to change your older evaluations**
    - [ ] Make evaluation success better (Instead of taking you to a different page)
    - [ ] Change building/item evaluations to be more like google sheets (ie. other evaluators listed, etc…)
        - [x] Other evaluator's evaluations listed
        - [ ] All buildings/items listed
- **<ins>Graphs</ins>**
    - [ ] Create historical records of nation/company assets (Total assets, liquid, items, buildings, other assets)
    - [ ] Individual nation/company graphs in their balance sheets
        - [ ] Total assets, liquid, items, buildings, other assets graphs over time
    - [ ] Pie chart of total assets of all nations (To show breakup of total world wealth)
    - [ ] **Bar chart of current assets by nation** 
        - [ ] Total assets, liquid, items, buildings, other assets graphs by nation
    - [ ] **Line graph of assets over time by nation**
        - [ ] Total assets, liquid, items, buildings, other assets graphs by nation by time
    - [ ] Size of nation stuff
        - [ ] Create historical records for size of nation data
        - [ ] Size of nation over time graph
            - [ ] Total territories, Main territories, far colonies, near colonies
- **<ins>Data Entry</ins>**
    - [X] **Item audit input page**
        - [x] Add any item for a given nation using a system like how items are displayed in balance sheets
        - [x] Add items and liquid assets on the same page
        - [X] Input more items without having to manually calculate sum (ie. it auto adds the amount inputed to the sum)
        - [X] Add shortcuts for stacks, blocks, stacks of blocks, small stacks
        - [X] Ablility to change the total for item/liquid asset in case I made a mistake
        - [X] Easily switch between nations and LiquidAssetContainers
    - [ ] **Add new/update building page**
        - [ ] Be able to delete destroyed buildings
        - [ ] Be able to search for existing buildings (narrows down list as you type more letters)
- **<ins>Player Viewer</ins>**
    - [ ] Display Extra Stats
        - [X] Location
        - [X] Death Location
        - [X] Hearts
        - [ ] Xp
    - [ ] Full shulker box viewing 
        - [X] Fix shulker boxes from displaying incorrectly
        - [X] Add shulker box preview
        - [X] Fix shulker box incorrect data
        - [ ] Fix shulker name overflow
    - [X] Enchantment Glint
    - [ ] De-Lag enchantment glints
    - [X] Add Rarity
    - [X] Fix Written Books
    - [X] Fix Model Viewer
    - [ ] Fix Potions and Tipped arrows
        - [ ] Add potion efffects and durations
        - [ ] Change potion and arrow colors
    - [ ] Add extra data to various items
        - [ ] Goat Horns
        - [ ] Ominous Bottles
        - [ ] Armor Trims
        - [ ] Music Disks
        - [ ] Suspicious Stew
    - [ ] Add durability
- **<ins>Misc.</ins>**
    - [ ] Sort buildings
        - [X] Sort by nation
        - [X] Sort by territory
        - [X] Sort by year
        - [ ] Sort by building price
    - [ ] **Overall info page**
        - [X] Per nation Average Height & # of Buildings info
        - [X] Per nation # of buildings built per year
        - [X] Total # of buildings per nation
        - [X] Per territory Average Height & # of Buildings info
        - [ ] Up and coming territories
    - [X] **Currency converter (ex: convert 42 emeralds and 58 copper to diamonds)**
    - [X] Item price calculator (Select items, see the price of them)
    - [ ] Architectural Styles stuff
    - [ ] Realty Commision?
    - [ ] Reid's stuff
        - [ ] Credit score?
        - [ ] Amortization Schedule?
        - [ ] Inflation calculator?
        - [ ] Change base currency (ex: change all values to gold or netherite)?
    - [ ] Display map/maps?
        - [ ] **Interactive map that shows buildings (Using coordinates)**
            - [x] Convert coordinates to x, inverse z
            - [x] Color data points to each nation
            - [x] Add data for each building when data is clicked on
            - [x] Filter out nether/end buildings
            - [ ] Extended map to show more land
        - [ ] Button that displays railroad/infrastructure routes
        - [X] Somehow display historical/informative maps
- **<ins>Records Document</ins>**
    - [x] UN Charter & amendments
        - [x] Past charters
    - [x] Resolutions
        - [x] Void/repealed resolutions
        - [x] Images
        - [x] Amendments
        - [x] Ability to link to individual resolution
    - [x] Treaties
        - [x] Images
        - [x] Ability to link to individual treaty
    - [x] Court Cases
        - [x] Images/videos
        - [x] Ability to link to individual court case
    - [x] Executive Orders
    - [ ] Misc.
        - [x] Recognized Alliances
        - [x] Declarations of War
        - [x] National Constitutions
        - [ ] Buisnesses and Shops
        - [ ] Aternos Games
        - [ ] Medal of Papa Quinn
        - [X] Petitions
        - [ ] UN Staff
        - [ ] Historical UN Sessions
        - [ ] Name Changes
