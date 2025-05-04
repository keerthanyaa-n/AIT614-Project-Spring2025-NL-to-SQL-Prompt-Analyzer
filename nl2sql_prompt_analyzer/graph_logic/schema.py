REAL_WORLD_SCHEMA_DEFINITION = [
        {
            "table_name": "prod_catalog",
            "description": "Stores details about vehicle models offered.",
            "columns": """prdid integer PRIMARY KEY -- Unique identifier for a car model
        mdlnm text NOT NULL -- Specific model name
        bodystylecd text -- e.g., 'SED', 'SUV', 'TRK'
        bsmrp numeric(12, 2) -- Manufacturer's Suggested Retail Price (Base)
        lnchyr integer -- Model year""",
            "foreign_keys": []
        },
        {
            "table_name": "vendor_master",
            "description": "Stores information about suppliers/vendors.",
            "columns": """vndrid integer PRIMARY KEY -- Supplier Unique Identifier
        vname text NOT NULL -- Supplier Company Name
        pocname text -- Point of Contact Person
        pocemail text -- Contact Email Address
        vcity text -- Supplier City
        vstate character(2) -- Supplier State (2-letter code)""",
            "foreign_keys": []
        },
        {
            "table_name": "part_inventory",
            "description": "Inventory of components and parts.",
            "columns": """prtsku integer PRIMARY KEY -- Stock Keeping Unit for the part
        prtnm text NOT NULL -- Name of the component/part
        prtdtl text -- Detailed Description (Optional)
        prtcat text -- Component Category Code (e.g., 'ENG', 'ELEC', 'CHAS')
        stdcost numeric(10, 2) -- Standard or Average Cost per unit
        matspec text -- Material Specification Code""",
            "foreign_keys": []
        },
        {
            "table_name": "client_registry",
            "description": "Master list of customers/clients.",
            "columns": """clntid integer PRIMARY KEY -- Unique Customer Identifier
        fstnm text -- First Name
        lstnm text -- Last Name
        orgnm text -- Company/Organization Name (if applicable)
        email text UNIQUE -- Email Address
        phone text -- Primary Phone Number
        regdt date DEFAULT CURRENT_DATE -- Date customer was registered""",
            "foreign_keys": []
        },
        {
            "table_name": "client_addresses",
            "description": "Stores customer addresses. References client_registry via clntref.",
            "columns": """addrid integer PRIMARY KEY AUTOINCREMENT -- Unique address ID
        clntref integer NOT NULL -- Link to the Client Registry (FK ClntId)
        addrtyp text DEFAULT 'PRI' -- e.g., 'PRI', 'BIL', 'SHP'
        addrln1 text -- Street Address Line 1
        city text -- City
        stateprov character(2) -- State Code
        postalcd text -- Zip or Postal Code""",
            "foreign_keys": [
            {"column": "clntref", "references_table": "client_registry", "references_column": "clntid"}
            ]
        },
        {
            "table_name": "site_directory",
            "description": "Stores information about physical company locations (factories, dealers, etc.).",
            "columns": """locid text PRIMARY KEY -- Short Code for Location (e.g., 'FAC01', 'DLNY', 'WHWST')
        locname text NOT NULL -- Full Name of the site
        loctype text NOT NULL -- 'FCTRY', 'DLR', 'WHSE', 'OFFC', 'SVC'
        loccity text -- Location City
        locstate character(2) -- Location State""",
            "foreign_keys": []
        },
        {
            "table_name": "org_departments",
            "description": "List of organizational departments. References personnel_roster via mgrref.",
            "columns": """dptcd text PRIMARY KEY -- Department Code (e.g., 'MFG', 'SAL', 'SVC', 'HR', 'FIN')
        dptname text NOT NULL -- Full Department Name
        mgrref integer -- Employee Ref of the department manager (FK to Personnel_Roster)""",
            "foreign_keys": [
            {"column": "mgrref", "references_table": "personnel_roster", "references_column": "empref"}
            ]
        },
        {
            "table_name": "personnel_roster",
            "description": "Stores employee information. References org_departments via dptref, site_directory via worklocid, and self via supref.",
            "columns": """empref integer PRIMARY KEY -- Employee Identifier
        fname text NOT NULL -- First Name
        lname text NOT NULL -- Last Name
        jobcd text -- Job Title Code or Identifier
        dptref text NOT NULL -- Department Code (FK to Org_Departments)
        hiredate date NOT NULL -- Date of Hire
        paytype text CHECK (PayType IN ('SAL', 'HRLY', 'CON')) -- Pay Type ('SAL', 'HRLY', 'CON')
        payamt numeric(10, 2) -- Annual Salary or Hourly Rate
        corpemail text UNIQUE -- Company Email Address
        workphone text -- Work Phone Number
        worklocid text -- Primary Site Code (FK to Site_Directory)
        supref integer -- Supervisor's Employee Ref (Self-ref FK)
        isactiveflg boolean DEFAULT true -- Is the employee currently employed?""",
            "foreign_keys": [
            {"column": "dptref", "references_table": "org_departments", "references_column": "dptcd"},
            {"column": "worklocid", "references_table": "site_directory", "references_column": "locid"},
            {"column": "supref", "references_table": "personnel_roster", "references_column": "empref"}
            ]
        },
        {
            "table_name": "vehicle_inventory",
            "description": "Inventory of specific vehicle instances identified by VIN. References prod_catalog via prdid and site_directory via currlocid.",
            "columns": """vehvin text PRIMARY KEY -- Vehicle Identification Number (Unique)
        prdid integer NOT NULL -- Link to product model (FK to Prod_Catalog)
        proddate date -- Date the specific vehicle was manufactured
        currlocid text -- Current location site code (FK to Site_Directory)
        vehstat text DEFAULT 'INV' -- Status e.g., 'INV', 'SOLD', 'LSED', 'SVC'
        colorcd text -- Vehicle color code
        actlmsrp numeric(12, 2) -- Actual MSRP for this specific VIN""",
            "foreign_keys": [
            {"column": "prdid", "references_table": "prod_catalog", "references_column": "prdid"},
            {"column": "currlocid", "references_table": "site_directory", "references_column": "locid"}
            ]
        },
        {
            "table_name": "prod_features",
            "description": "Master list of available product features and options.",
            "columns": """featcd text PRIMARY KEY -- Code for the feature (e.g., 'SNRF', 'NAV', 'AWD')
        featname text NOT NULL -- Descriptive name
        featdesc text -- Longer description
        optcost numeric(8, 2) -- Additional cost for this feature/option""",
            "foreign_keys": []
        },
        {
            "table_name": "skill_codes",
            "description": "Master list of employee skills.",
            "columns": """skllcd text PRIMARY KEY -- Unique code for the skill (e.g., 'WLD-TIG', 'ENG-DIAG', 'CRM')
        skllname text NOT NULL -- Descriptive name of the skill
        skllcat text -- Broader category (e.g., 'MFG', 'DIAG', 'SALES', 'IT')""",
            "foreign_keys": []
        },
        {
            "table_name": "promo_campaigns",
            "description": "Master list of sales promotions and campaigns.",
            "columns": """prmocd text PRIMARY KEY -- Unique code for the promotion (e.g., 'SUM25', 'LOYAL10')
        prmoname text NOT NULL -- Name of the promotion
        prmodesc text -- Description of the offer
        dscnttype text CHECK (DscntType IN ('PERC', 'FIXED')) -- Discount Type ('PERC', 'FIXED')
        dscntval numeric(8, 2) NOT NULL -- Percentage or fixed amount
        startdt date NOT NULL -- Promotion start date
        enddt date NOT NULL -- Promotion end date
        activeflg boolean DEFAULT true -- Is the promotion currently active?""",
            "foreign_keys": []
        },
        {
            "table_name": "prod_bom",
            "description": "Bill of Materials, linking products to required parts (Many-to-Many). References prod_catalog via prdid and part_inventory via prtid.",
            "columns": """prdid integer PRIMARY KEY -- Part of composite PK (FK to Prod_Catalog)
        prtid integer PRIMARY KEY -- Part of composite PK (FK to Part_Inventory)
        qtyperassy integer NOT NULL -- Quantity of this part needed per assembly""",
            "foreign_keys": [
            {"column": "prdid", "references_table": "prod_catalog", "references_column": "prdid"},
            {"column": "prtid", "references_table": "part_inventory", "references_column": "prtsku"}
            ]
        },
        {
            "table_name": "mfg_workorders",
            "description": "Manufacturing work orders for building products. References prod_catalog via tgtprd.",
            "columns": """wo_ref integer PRIMARY KEY -- Work Order Identifier
        tgtprd integer NOT NULL -- Product to be built (FK to Prod_Catalog)
        buildqty integer NOT NULL -- Quantity to manufacture
        issdt date DEFAULT CURRENT_DATE -- Date WO was created
        estcompdt date -- Estimated Due Date
        wo_stat text CHECK (WO_Stat IN ('PEND', 'INPR', 'COMP', 'CANC')) -- Status ('PEND', 'INPR', 'COMP', 'CANC')""",
            "foreign_keys": [
            {"column": "tgtprd", "references_table": "prod_catalog", "references_column": "prdid"}
            ]
        },
        {
            "table_name": "sales_hdrs",
            "description": "Header information for customer sales orders. References client_registry via clntref and personnel_roster via salesrepref.",
            "columns": """so_ref integer PRIMARY KEY -- Sales Order Number
        clntref integer NOT NULL -- Customer placing the order (FK to Client_Registry)
        ordts timestamp without time zone DEFAULT CURRENT_TIMESTAMP -- Timestamp order was placed
        ordstat text CHECK (OrdStat IN ('PLACED', 'PROC', 'SHIP', 'DLVR', 'CANC')) -- Order Status
        ordtotal numeric(14, 2) -- Calculated total value
        salesrepref integer -- Employee responsible for sale (FK to Personnel_Roster)""",
            "foreign_keys": [
            {"column": "clntref", "references_table": "client_registry", "references_column": "clntid"},
            {"column": "salesrepref", "references_table": "personnel_roster", "references_column": "empref"}
            ]
        },
        {
            "table_name": "sales_lines",
            "description": "Line items for each sales order. References sales_hdrs via so_ref and prod_catalog via prdid.",
            "columns": """solineid integer PRIMARY KEY AUTOINCREMENT -- Unique line item ID
        so_ref integer NOT NULL -- Link to Sales Order Header (FK to Sales_Hdrs)
        prdid integer NOT NULL -- Product being ordered (FK to Prod_Catalog)
        qty integer NOT NULL -- Quantity ordered
        unitprc numeric(12, 2) -- Price per unit
        linetot numeric(14, 2) -- Calculated line total""",
            "foreign_keys": [
            {"column": "so_ref", "references_table": "sales_hdrs", "references_column": "so_ref"},
            {"column": "prdid", "references_table": "prod_catalog", "references_column": "prdid"}
            ]
        },
        {
            "table_name": "prod_feature_avail",
            "description": "Links available features/options to product models (Many-to-Many). References prod_catalog via prdid and prod_features via featcd.",
            "columns": """prdid integer PRIMARY KEY -- Part of composite PK (FK to Prod_Catalog)
        featcd text PRIMARY KEY -- Part of composite PK (FK to Prod_Features)
        isstdflg boolean DEFAULT false -- Is this feature standard on this model?
        optprc numeric(8, 2) -- Price if added as an option""",
            "foreign_keys": [
            {"column": "prdid", "references_table": "prod_catalog", "references_column": "prdid"},
            {"column": "featcd", "references_table": "prod_features", "references_column": "featcd"}
            ]
        },
        {
            "table_name": "vehicle_config",
            "description": "Links installed features/options to specific vehicles (Many-to-Many). References vehicle_inventory via vinref and prod_features via featcd.",
            "columns": """vinref text PRIMARY KEY -- Part of composite PK (FK to Vehicle_Inventory)
        featcd text PRIMARY KEY -- Part of composite PK (FK to Prod_Features)
        installts timestamp without time zone DEFAULT CURRENT_TIMESTAMP -- Timestamp feature was recorded""",
            "foreign_keys": [
            {"column": "vinref", "references_table": "vehicle_inventory", "references_column": "vehvin"},
            {"column": "featcd", "references_table": "prod_features", "references_column": "featcd"}
            ]
        },
        {
            "table_name": "svc_log",
            "description": "Log of service records and maintenance events for vehicles. References vehicle_inventory via vinref, client_registry via clntref, site_directory via svclocid, and personnel_roster via techref.",
            "columns": """svctktid integer PRIMARY KEY AUTOINCREMENT -- Unique service ticket ID
        vinref text NOT NULL -- VIN of vehicle serviced (FK to Vehicle_Inventory)
        clntref integer -- Customer who brought it in (FK to Client_Registry)
        svclocid text NOT NULL -- Site Code where service performed (FK to Site_Directory)
        techref integer -- Employee who performed service (FK to Personnel_Roster)
        svcdt date NOT NULL -- Date of service
        svccd text -- Service Code (e.g., 'OIL', 'WRNTY', 'REPAIR')
        svcdesc text -- Details of work performed
        lbrhrs numeric(5, 2) -- Labor hours charged
        svccost numeric(10, 2) -- Total cost of the service""",
            "foreign_keys": [
            {"column": "vinref", "references_table": "vehicle_inventory", "references_column": "vehvin"},
            {"column": "clntref", "references_table": "client_registry", "references_column": "clntid"},
            {"column": "svclocid", "references_table": "site_directory", "references_column": "locid"},
            {"column": "techref", "references_table": "personnel_roster", "references_column": "empref"}
            ]
        },
        {
            "table_name": "svc_partsused",
            "description": "Links parts used from inventory to specific service records (Many-to-Many). References svc_log via svctktid and part_inventory via prtid.",
            "columns": """svctktid integer PRIMARY KEY -- Part of composite PK (FK to Svc_Log)
        prtid integer PRIMARY KEY -- Part of composite PK (FK to Part_Inventory)
        qty integer NOT NULL -- Quantity of the part used
        costbasis numeric(10, 2) -- Cost of the part when used""",
            "foreign_keys": [
            {"column": "svctktid", "references_table": "svc_log", "references_column": "svctktid"},
            {"column": "prtid", "references_table": "part_inventory", "references_column": "prtsku"}
            ]
        },
        {
            "table_name": "lease_contracts",
            "description": "Stores details of vehicle lease agreements. References vehicle_inventory via vinref and client_registry via clntref.",
            "columns": """lseid integer PRIMARY KEY -- Unique lease identifier
        vinref text NOT NULL UNIQUE -- VIN of the leased vehicle (FK to Vehicle_Inventory)
        clntref integer NOT NULL -- Customer leasing (FK to Client_Registry)
        startdt date NOT NULL -- Lease start date
        enddt date NOT NULL -- Lease end date
        mnthpay numeric(8, 2) -- Monthly payment amount
        lsestat text DEFAULT 'ACTV' -- Lease status ('ACTV', 'END', 'DFLT')""",
            "foreign_keys": [
            {"column": "vinref", "references_table": "vehicle_inventory", "references_column": "vehvin"},
            {"column": "clntref", "references_table": "client_registry", "references_column": "clntid"}
            ]
        },
        {
            "table_name": "lease_installments",
            "description": "Records individual payments made for lease contracts. References lease_contracts via lseref.",
            "columns": """pmtid integer PRIMARY KEY AUTOINCREMENT -- Unique payment ID
        lseref integer NOT NULL -- Link to the Lease Contract (FK to Lease_Contracts)
        pmtdt date NOT NULL -- Date payment was made
        amt numeric(8, 2) -- Amount paid
        pmtmeth text -- Payment Method (e.g., 'ACH', 'CC', 'CHK')""",
            "foreign_keys": [
            {"column": "lseref", "references_table": "lease_contracts", "references_column": "lseid"}
            ]
        },
        {
            "table_name": "loyalty_ledger",
            "description": "Tracks customer loyalty points transactions. References client_registry via clntref and sales_hdrs via soref.",
            "columns": """trnsid integer PRIMARY KEY AUTOINCREMENT -- Unique transaction ID
        clntref integer NOT NULL -- Customer involved (FK to Client_Registry)
        trnstyp text NOT NULL -- Transaction Type ('EARN', 'REDEEM', 'ADJ')
        pts integer NOT NULL -- Points earned (+) or redeemed (-)
        trns_ts timestamp without time zone DEFAULT CURRENT_TIMESTAMP -- Transaction timestamp
        soref integer -- Optional link to a Sales Order (FK to Sales_Hdrs)
        trnsnotes text -- Notes about the transaction""",
            "foreign_keys": [
            {"column": "clntref", "references_table": "client_registry", "references_column": "clntid"},
            {"column": "soref", "references_table": "sales_hdrs", "references_column": "so_ref"}
            ]
        },
        {
            "table_name": "employee_skills",
            "description": "Links employees to their skills (Many-to-Many). References personnel_roster via empref and skill_codes via skllcd.",
            "columns": """empref integer PRIMARY KEY -- Part of composite PK (FK to Personnel_Roster)
        skllcd text PRIMARY KEY -- Part of composite PK (FK to Skill_Codes)
        sklllvl integer -- Optional: Proficiency level (e.g., 1-5)
        certdt date -- Optional: Date certification achieved""",
            "foreign_keys": [
            {"column": "empref", "references_table": "personnel_roster", "references_column": "empref"},
            {"column": "skllcd", "references_table": "skill_codes", "references_column": "skllcd"}
            ]
        },
        {
            "table_name": "part_suppliers",
            "description": "Links parts to the vendors who supply them (Many-to-Many). References part_inventory via prtid and vendor_master via vndrid.",
            "columns": """prtid integer PRIMARY KEY -- Part of composite PK (FK to Part_Inventory)
        vndrid integer PRIMARY KEY -- Part of composite PK (FK to Vendor_Master)
        vndrprtno text -- Supplier's specific part number (Optional)
        lt_days integer -- Typical lead time (Optional)
        supcost numeric(10, 2) -- Cost from this specific supplier
        prefsupflg boolean DEFAULT false -- Is this the preferred supplier?""",
            "foreign_keys": [
            {"column": "prtid", "references_table": "part_inventory", "references_column": "prtsku"},
            {"column": "vndrid", "references_table": "vendor_master", "references_column": "vndrid"}
            ]
        },
        {
            "table_name": "applied_order_promos",
            "description": "Links applied promotions to specific sales orders (Many-to-Many). References sales_hdrs via so_ref and promo_campaigns via prmocd.",
            "columns": """so_ref integer PRIMARY KEY -- Part of composite PK (FK to Sales_Hdrs)
        prmocd text PRIMARY KEY -- Part of composite PK (FK to Promo_Campaigns)
        dscntamt numeric(10, 2) -- Actual discount amount applied
        applyts timestamp without time zone DEFAULT CURRENT_TIMESTAMP -- Timestamp promo was applied""",
            "foreign_keys": [
            {"column": "so_ref", "references_table": "sales_hdrs", "references_column": "so_ref"},
            {"column": "prmocd", "references_table": "promo_campaigns", "references_column": "prmocd"}
            ]
        },
        {
            "table_name": "inventorylevels",
            "description": "Tracks inventory levels of products OR components at specific locations. References locations, products, components.",
            "columns": """inventoryid integer PRIMARY KEY AUTOINCREMENT
            locationid integer NOT NULL
            productid integer
            componentid integer
            quantityonhand integer NOT NULL
            lastupdated timestamp without time zone NOT NULL
            CONSTRAINT check_product_or_component CHECK ((ProductID IS NULL AND ComponentID IS NOT NULL) OR (ProductID IS NOT NULL AND ComponentID IS NULL))""",
            "foreign_keys": [
                {"column": "locationid", "references_table": "locations", "references_column": "locationid"},
                {"column": "productid", "references_table": "products", "references_column": "productid"},
                {"column": "componentid", "references_table": "components", "references_column": "componentid"}
            ]
        }
    ]

BENCHMARK_SCHEMA_DEFINITION= [
{
    "table_name": "Addresses",
    "description": "Stores various types of addresses (Primary, Shipping, Billing, Home, Work, Site).",
    "columns": """AddressID INTEGER PRIMARY KEY
StreetAddress TEXT NOT NULL
City TEXT NOT NULL
State TEXT NOT NULL
ZipCode TEXT NOT NULL
Country TEXT DEFAULT 'USA'
AddressType TEXT""",
    "foreign_keys": []
  },
  {
    "table_name": "Products",
    "description": "Catalog of vehicle models offered.",
    "columns": """ProductID INTEGER PRIMARY KEY
ModelName TEXT NOT NULL
BodyStyle TEXT NOT NULL
BasePrice DECIMAL(10, 2) NOT NULL
LaunchYear INTEGER NOT NULL
IsActive BOOLEAN NOT NULL""",
    "foreign_keys": []
  },
  {
    "table_name": "Features",
    "description": "Master list of available vehicle features.",
    "columns": """FeatureID INTEGER PRIMARY KEY
FeatureName TEXT NOT NULL
FeatureType TEXT NOT NULL
AdditionalCost DECIMAL(10, 2) NOT NULL""",
    "foreign_keys": []
  },
  {
    "table_name": "ProductFeatures",
    "description": "Links Products to their available Features (Many-to-Many). References Products and Features.",
    "columns": """ProductID INTEGER PRIMARY KEY -- Part of composite PK
FeatureID INTEGER PRIMARY KEY -- Part of composite PK""",
    "foreign_keys": [
      {"column": "ProductID", "references_table": "Products", "references_column": "ProductID"},
      {"column": "FeatureID", "references_table": "Features", "references_column": "FeatureID"}
    ]
  },
  {
    "table_name": "Suppliers",
    "description": "Information about parts suppliers. References Addresses via PrimaryAddressID.",
    "columns": """SupplierID INTEGER PRIMARY KEY
SupplierName TEXT NOT NULL
ContactPerson TEXT
ContactEmail TEXT
PrimaryAddressID INTEGER""",
    "foreign_keys": [
      {"column": "PrimaryAddressID", "references_table": "Addresses", "references_column": "AddressID"}
    ]
  },
  {
    "table_name": "Components",
    "description": "Details about individual parts/components. References Suppliers via SupplierID.",
    "columns": """ComponentID INTEGER PRIMARY KEY
ComponentName TEXT NOT NULL
Description TEXT
Category TEXT NOT NULL
UnitCost DECIMAL(10, 2) NOT NULL
Material TEXT
SupplierID INTEGER""",
    "foreign_keys": [
      {"column": "SupplierID", "references_table": "Suppliers", "references_column": "SupplierID"}
    ]
  },
  {
    "table_name": "ProductComponents",
    "description": "Bill of Materials, linking Products to Components (Many-to-Many). References Products and Components.",
    "columns": """ProductID INTEGER PRIMARY KEY -- Part of composite PK
ComponentID INTEGER PRIMARY KEY -- Part of composite PK
QuantityRequired INTEGER NOT NULL""",
    "foreign_keys": [
      {"column": "ProductID", "references_table": "Products", "references_column": "ProductID"},
      {"column": "ComponentID", "references_table": "Components", "references_column": "ComponentID"}
    ]
  },
  {
    "table_name": "Locations",
    "description": "Physical company locations (Factory, Dealership, Office, etc.). References Addresses via PrimaryAddressID.",
    "columns": """LocationID INTEGER PRIMARY KEY
LocationName TEXT NOT NULL
LocationType TEXT NOT NULL -- ('Factory', 'Dealership', 'Office', 'Warehouse', 'Service Center')
PrimaryAddressID INTEGER""",
    "foreign_keys": [
      {"column": "PrimaryAddressID", "references_table": "Addresses", "references_column": "AddressID"}
    ]
  },
  {
    "table_name": "Departments",
    "description": "Organizational departments. References Employees via ManagerID.",
    "columns": """DepartmentID INTEGER PRIMARY KEY
DepartmentName TEXT NOT NULL
ManagerID INTEGER""",
    "foreign_keys": [
      {"column": "ManagerID", "references_table": "Employees", "references_column": "EmployeeID"}
    ]
  },
  {
    "table_name": "Employees",
    "description": "Employee information. References Departments, Locations, Addresses, and self (for Supervisor).",
    "columns": """EmployeeID INTEGER PRIMARY KEY
FirstName TEXT NOT NULL
LastName TEXT NOT NULL
JobTitle TEXT NOT NULL
DepartmentID INTEGER
HireDate DATE NOT NULL
TerminationDate DATE
Status TEXT NOT NULL -- ('Active', 'Terminated', 'On Leave')
SalaryOrRate DECIMAL(10, 2) NOT NULL
PayType TEXT NOT NULL -- ('Salary', 'Hourly')
Email TEXT
WorkPhone TEXT
LocationID INTEGER
HomeAddressID INTEGER
SupervisorID INTEGER""",
    "foreign_keys": [
      {"column": "DepartmentID", "references_table": "Departments", "references_column": "DepartmentID"},
      {"column": "LocationID", "references_table": "Locations", "references_column": "LocationID"},
      {"column": "HomeAddressID", "references_table": "Addresses", "references_column": "AddressID"},
      {"column": "SupervisorID", "references_table": "Employees", "references_column": "EmployeeID"}
    ]
  },
  {
    "table_name": "WorkOrders",
    "description": "Manufacturing work orders. References Products via ProductID.",
    "columns": """WorkOrderID INTEGER PRIMARY KEY
ProductID INTEGER NOT NULL
Quantity INTEGER NOT NULL
DateCreated DATE NOT NULL
DueDate DATE
Status TEXT NOT NULL -- ('Pending', 'In Progress', 'Completed', 'Cancelled')""",
    "foreign_keys": [
      {"column": "ProductID", "references_table": "Products", "references_column": "ProductID"}
    ]
  },
  {
    "table_name": "Customers",
    "description": "Customer details. References Addresses via PrimaryAddressID.",
    "columns": """CustomerID INTEGER PRIMARY KEY
FirstName TEXT
LastName TEXT
CompanyName TEXT
Email TEXT
Phone TEXT
PrimaryAddressID INTEGER
RegistrationDate DATE NOT NULL
LoyaltyPointsBalance INTEGER DEFAULT 0""",
    "foreign_keys": [
      {"column": "PrimaryAddressID", "references_table": "Addresses", "references_column": "AddressID"}
    ]
  },
  {
    "table_name": "Vehicles",
    "description": "Specific vehicle instances (VINs). References Products, WorkOrders, and Customers.",
    "columns": """VehicleID INTEGER PRIMARY KEY
VIN TEXT UNIQUE NOT NULL
ProductID INTEGER NOT NULL
ManufactureDate DATE NOT NULL
Color TEXT
WorkOrderID INTEGER
CurrentMileage INTEGER
LastServiceDate DATE
CurrentStatus TEXT NOT NULL -- ('Inventory', 'Sold', 'Leased', 'Rented', 'In Service', 'Decommissioned')
CurrentHolderCustomerID INTEGER""",
    "foreign_keys": [
      {"column": "ProductID", "references_table": "Products", "references_column": "ProductID"},
      {"column": "WorkOrderID", "references_table": "WorkOrders", "references_column": "WorkOrderID"},
      {"column": "CurrentHolderCustomerID", "references_table": "Customers", "references_column": "CustomerID"}
    ]
  },
  {
    "table_name": "VehicleFeatures",
    "description": "Links installed Features to specific Vehicles (Many-to-Many). References Vehicles and Features.",
    "columns": """VehicleID INTEGER PRIMARY KEY -- Part of composite PK
FeatureID INTEGER PRIMARY KEY -- Part of composite PK""",
    "foreign_keys": [
      {"column": "VehicleID", "references_table": "Vehicles", "references_column": "VehicleID"},
      {"column": "FeatureID", "references_table": "Features", "references_column": "FeatureID"}
    ]
  },
  {
    "table_name": "SalesOrders",
    "description": "Header information for sales orders. References Customers and Addresses.",
    "columns": """SalesOrderID INTEGER PRIMARY KEY
CustomerID INTEGER NOT NULL
OrderTimestamp TIMESTAMP NOT NULL
ShippingAddressID INTEGER
Status TEXT NOT NULL -- ('Placed', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
TotalAmount DECIMAL(10, 2)""",
    "foreign_keys": [
      {"column": "CustomerID", "references_table": "Customers", "references_column": "CustomerID"},
      {"column": "ShippingAddressID", "references_table": "Addresses", "references_column": "AddressID"}
    ]
  },
  {
    "table_name": "SalesOrderItems",
    "description": "Line items for sales orders. References SalesOrders and Vehicles.",
    "columns": """OrderItemID INTEGER PRIMARY KEY
SalesOrderID INTEGER NOT NULL
VehicleID INTEGER
Quantity INTEGER NOT NULL
AgreedPrice DECIMAL(10, 2) NOT NULL""",
    "foreign_keys": [
      {"column": "SalesOrderID", "references_table": "SalesOrders", "references_column": "SalesOrderID"},
      {"column": "VehicleID", "references_table": "Vehicles", "references_column": "VehicleID"}
    ]
  },
  {
    "table_name": "LeaseRentalAgreements",
    "description": "Details of lease or rental agreements. References Customers and Vehicles.",
    "columns": """AgreementID INTEGER PRIMARY KEY
CustomerID INTEGER NOT NULL
VehicleID INTEGER NOT NULL
AgreementType TEXT NOT NULL -- ('Lease', 'Rental')
StartDate DATE NOT NULL
EndDate DATE NOT NULL
MonthlyPayment DECIMAL(10, 2)
RentalRatePerDay DECIMAL(10, 2)
Status TEXT NOT NULL -- ('Active', 'Completed', 'Terminated Early', 'Pending')
Notes TEXT""",
    "foreign_keys": [
      {"column": "CustomerID", "references_table": "Customers", "references_column": "CustomerID"},
      {"column": "VehicleID", "references_table": "Vehicles", "references_column": "VehicleID"}
    ]
  },
  {
    "table_name": "ServiceRecords",
    "description": "Log of service events for vehicles. References Vehicles, Customers, Locations, and Employees.",
    "columns": """ServiceID INTEGER PRIMARY KEY
VehicleID INTEGER NOT NULL
CustomerID INTEGER NOT NULL
LocationID INTEGER NOT NULL
TechnicianID INTEGER
ServiceDate DATE NOT NULL
ServiceType TEXT NOT NULL
IsWarrantyClaim BOOLEAN NOT NULL
Notes TEXT
LaborHours DECIMAL(5, 2)
PartsCost DECIMAL(10, 2)
LaborCost DECIMAL(10, 2)
TotalCost DECIMAL(10, 2)
PointsEarned INTEGER""",
    "foreign_keys": [
      {"column": "VehicleID", "references_table": "Vehicles", "references_column": "VehicleID"},
      {"column": "CustomerID", "references_table": "Customers", "references_column": "CustomerID"},
      {"column": "LocationID", "references_table": "Locations", "references_column": "LocationID"},
      {"column": "TechnicianID", "references_table": "Employees", "references_column": "EmployeeID"}
    ]
  },
  {
    "table_name": "ServicePartsUsed",
    "description": "Links parts used to service records (Many-to-Many). References ServiceRecords and Components.",
    "columns": """ServiceID INTEGER PRIMARY KEY -- Part of composite PK
ComponentID INTEGER PRIMARY KEY -- Part of composite PK
QuantityUsed INTEGER NOT NULL
UnitPrice DECIMAL(10, 2) NOT NULL""",
    "foreign_keys": [
      {"column": "ServiceID", "references_table": "ServiceRecords", "references_column": "ServiceID"},
      {"column": "ComponentID", "references_table": "Components", "references_column": "ComponentID"}
    ]
  },
  {
    "table_name": "LoyaltyTransactions",
    "description": "Tracks customer loyalty points changes. References Customers, ServiceRecords, and LeaseRentalAgreements.",
    "columns": """TransactionID INTEGER PRIMARY KEY
CustomerID INTEGER NOT NULL
TransactionType TEXT NOT NULL -- ('Earned', 'Redeemed', 'Adjustment', 'Expired')
PointsChanged INTEGER NOT NULL
TransactionDate TIMESTAMP NOT NULL
RelatedServiceID INTEGER
RelatedAgreementID INTEGER
Notes TEXT""",
    "foreign_keys": [
      {"column": "CustomerID", "references_table": "Customers", "references_column": "CustomerID"},
      {"column": "RelatedServiceID", "references_table": "ServiceRecords", "references_column": "ServiceID"},
      {"column": "RelatedAgreementID", "references_table": "LeaseRentalAgreements", "references_column": "AgreementID"}
    ]
  },
  {
    "table_name": "InventoryLevels",
    "description": "Tracks inventory levels of products OR components at locations. References Locations, Products, and Components.",
    "columns": """InventoryID INTEGER PRIMARY KEY
LocationID INTEGER NOT NULL
ProductID INTEGER
ComponentID INTEGER
QuantityOnHand INTEGER NOT NULL
LastUpdated TIMESTAMP NOT NULL
CONSTRAINT check_product_or_component CHECK ((ProductID IS NULL AND ComponentID IS NOT NULL) OR (ProductID IS NOT NULL AND ComponentID IS NULL))""",
    "foreign_keys": [
      {"column": "LocationID", "references_table": "Locations", "references_column": "LocationID"},
      {"column": "ProductID", "references_table": "Products", "references_column": "ProductID"},
      {"column": "ComponentID", "references_table": "Components", "references_column": "ComponentID"}
    ]
  }
]
