-- Consolidated Schema Script (Car Manufacturing - 23 Tables)
-- Version with Complex Attribute Naming, M:M Relationships
-- Corrected for PostgreSQL (using SERIAL for auto-incrementing keys)

-- Basic Master Data Tables --

-- 1. Product Catalog / Models
CREATE TABLE Prod_Catalog (
    PrdId INTEGER PRIMARY KEY,       -- Product Identifier
    MdlNm TEXT NOT NULL,             -- Vehicle Model Designation
    BodyStyleCd TEXT,                -- e.g., 'SED', 'SUV', 'TRK'
    BsMRP DECIMAL(12, 2),            -- Manufacturer's Suggested Retail Price (Base)
    LnchYr INTEGER                   -- Year Model Introduced
);

-- 2. Suppliers / Vendors
CREATE TABLE Vendor_Master (
    VndrId INTEGER PRIMARY KEY,      -- Supplier Unique Identifier
    VName TEXT NOT NULL,             -- Supplier Company Name
    POCName TEXT,                    -- Point of Contact Person
    POCEmail TEXT,                   -- Contact Email Address
    VCity TEXT,                      -- Supplier City
    VState CHAR(2)                   -- Supplier State (2-letter code)
);

-- 3. Components / Parts Inventory (MODIFIED: No direct supplier link)
CREATE TABLE Part_Inventory (
    PrtSKU INTEGER PRIMARY KEY,      -- Stock Keeping Unit for the part
    PrtNm TEXT NOT NULL,             -- Name of the component/part
    PrtDtl TEXT,                     -- Detailed Description (Optional)
    PrtCat TEXT,                     -- Component Category Code (e.g., 'ENG', 'ELEC', 'CHAS')
    StdCost DECIMAL(10, 2),          -- Standard or Average Cost per unit
    MatSpec TEXT                     -- Material Specification Code
);

-- 4. Customers / Clients
CREATE TABLE Client_Registry (
    ClntId INTEGER PRIMARY KEY,      -- Unique Customer Identifier
    FstNm TEXT,                      -- First Name
    LstNm TEXT,                      -- Last Name
    OrgNm TEXT,                      -- Company/Organization Name (if applicable)
    Email TEXT UNIQUE,               -- Email Address
    Phone TEXT,                      -- Primary Phone Number
    RegDt DATE DEFAULT CURRENT_DATE  -- Date customer was registered
);

-- 5. Customer Addresses (Corrected for PostgreSQL)
CREATE TABLE Client_Addresses (
    AddrId SERIAL PRIMARY KEY,        -- Use SERIAL for auto-incrementing PK in PostgreSQL
    ClntRef INTEGER NOT NULL,        -- Link to the Client Registry (FK ClntId)
    AddrTyp TEXT DEFAULT 'PRI',      -- e.g., 'PRI', 'BIL', 'SHP'
    AddrLn1 TEXT,                    -- Street Address Line 1
    City TEXT,                       -- City
    StateProv CHAR(2),               -- State Code
    PostalCd TEXT,                   -- Zip or Postal Code
    FOREIGN KEY (ClntRef) REFERENCES Client_Registry(ClntId)
);

-- 6. Physical Locations / Sites
CREATE TABLE Site_Directory (
    LocId TEXT PRIMARY KEY,          -- Short Code for Location (e.g., 'FAC01', 'DLNY', 'WHWST')
    LocName TEXT NOT NULL,           -- Full Name of the site
    LocType TEXT NOT NULL,           -- 'FCTRY', 'DLR', 'WHSE', 'OFFC', 'SVC'
    LocCity TEXT,
    LocState CHAR(2)
);

-- 7. Departments / Business Units
CREATE TABLE Org_Departments (
    DptCd TEXT PRIMARY KEY,          -- Department Code (e.g., 'MFG', 'SAL', 'SVC', 'HR', 'FIN')
    DptName TEXT NOT NULL,           -- Full Department Name
    MgrRef INTEGER                   -- Employee Ref of the department manager (FK EmpRef added via ALTER TABLE later)
);

-- 8. Employees / Personnel
CREATE TABLE Personnel_Roster (
    EmpRef INTEGER PRIMARY KEY,      -- Employee Identifier
    FName TEXT NOT NULL,
    LName TEXT NOT NULL,
    JobCd TEXT,                      -- Job Title Code or Identifier
    DptRef TEXT NOT NULL,            -- Department Code the employee belongs to (FK DptCd)
    HireDate DATE NOT NULL,          -- Date of Hire
    PayType TEXT                     -- 'SAL', 'HRLY', 'CON'
      CHECK (PayType IN ('SAL', 'HRLY', 'CON')),
    PayAmt DECIMAL(10, 2),           -- Annual Salary or Hourly Rate
    CorpEmail TEXT UNIQUE,           -- Company Email Address
    WorkPhone TEXT,                  -- Work Phone Number
    WorkLocId TEXT,                  -- Primary Site Code where the employee works (FK LocId)
    SupRef INTEGER,                  -- Employee Ref of their direct supervisor (Nullable, Self-ref FK EmpRef)
    IsActiveFlg BOOLEAN DEFAULT TRUE, -- Is the employee currently employed? (Flag)
    FOREIGN KEY (DptRef) REFERENCES Org_Departments(DptCd),
    FOREIGN KEY (WorkLocId) REFERENCES Site_Directory(LocId),
    FOREIGN KEY (SupRef) REFERENCES Personnel_Roster(EmpRef) -- Self-referencing FK
);

-- 9. Vehicles (Specific Instances)
CREATE TABLE Vehicle_Inventory (
    VehVIN TEXT PRIMARY KEY,         -- Vehicle Identification Number (Unique)
    PrdId INTEGER NOT NULL,          -- Which product model this VIN corresponds to (FK PrdId)
    ProdDate DATE,                   -- Date the specific vehicle was manufactured
    CurrLocId TEXT,                  -- Site Code where the vehicle is currently located (FK LocId)
    VehStat TEXT DEFAULT 'INV',      -- e.g., 'INV', 'SOLD', 'LSED', 'SVC'
    ColorCd TEXT,
    ActlMSRP DECIMAL(12, 2),         -- MSRP for this specific VIN (may differ from base)
    FOREIGN KEY (PrdId) REFERENCES Prod_Catalog(PrdId),
    FOREIGN KEY (CurrLocId) REFERENCES Site_Directory(LocId)
);

-- 10. Product Features / Options Master List
CREATE TABLE Prod_Features (
    FeatCd TEXT PRIMARY KEY,         -- Code for the feature (e.g., 'SNRF', 'NAV', 'AWD')
    FeatName TEXT NOT NULL,          -- Descriptive name
    FeatDesc TEXT,                   -- Longer description
    OptCost DECIMAL(8, 2)            -- Additional cost for this feature/option
);

-- 11. Skills Master List
CREATE TABLE Skill_Codes (
    SkllCd TEXT PRIMARY KEY,         -- Unique code for the skill (e.g., 'WLD-TIG', 'ENG-DIAG', 'CRM')
    SkllName TEXT NOT NULL,          -- Descriptive name of the skill
    SkllCat TEXT                     -- Broader category (e.g., 'MFG', 'DIAG', 'SALES', 'IT')
);

-- 12. Promotions Master List
CREATE TABLE Promo_Campaigns (
    PrmoCd TEXT PRIMARY KEY,         -- Unique code for the promotion (e.g., 'SUM25', 'LOYAL10')
    PrmoName TEXT NOT NULL,          -- Name of the promotion
    PrmoDesc TEXT,                   -- Description of the offer
    DscntType TEXT                   -- 'PERC', 'FIXED'
        CHECK (DscntType IN ('PERC', 'FIXED')),
    DscntVal DECIMAL(8, 2) NOT NULL, -- Percentage (e.g., 10.00) or fixed amount (e.g., 50.00)
    StartDt DATE NOT NULL,
    EndDt DATE NOT NULL,
    ActiveFlg BOOLEAN DEFAULT TRUE
);


-- Transactional / Linking Tables --

-- 13. Bill of Materials (Product Structure - M:M Parts <-> Products)
CREATE TABLE Prod_BOM (
    PrdId INTEGER NOT NULL,          -- Reference to Product Catalog (FK PrdId)
    PrtId INTEGER NOT NULL,          -- Reference to Part Inventory (FK PrtSKU)
    QtyPerAssy INTEGER NOT NULL,     -- Quantity of this part needed for one unit of the product
    PRIMARY KEY (PrdId, PrtId),
    FOREIGN KEY (PrdId) REFERENCES Prod_Catalog(PrdId),
    FOREIGN KEY (PrtId) REFERENCES Part_Inventory(PrtSKU)
);

-- 14. Manufacturing Work Orders
CREATE TABLE Mfg_WorkOrders (
    WO_Ref INTEGER PRIMARY KEY,      -- Work Order Identifier
    TgtPrd INTEGER NOT NULL,         -- Product to be built (FK PrdId)
    BuildQty INTEGER NOT NULL,       -- Quantity to manufacture
    IssDt DATE DEFAULT CURRENT_DATE, -- When the WO was created
    EstCompDt DATE,                  -- Estimated Due Date
    WO_Stat TEXT                     -- e.g., 'PEND', 'INPR', 'COMP', 'CANC'
       CHECK (WO_Stat IN ('PEND', 'INPR', 'COMP', 'CANC')),
    FOREIGN KEY (TgtPrd) REFERENCES Prod_Catalog(PrdId)
);

-- 15. Sales Orders Header
CREATE TABLE Sales_Hdrs (
    SO_Ref INTEGER PRIMARY KEY,      -- Sales Order Number
    ClntRef INTEGER NOT NULL,        -- Customer placing the order (FK ClntId)
    OrdTS TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When the order was placed
    OrdStat TEXT                     -- e.g., 'PLACED', 'PROC', 'SHIP', 'DLVR', 'CANC'
       CHECK (OrdStat IN ('PLACED', 'PROC', 'SHIP', 'DLVR', 'CANC')),
    OrdTotal DECIMAL(14, 2),         -- Calculated total value (might be updated later)
    SalesRepRef INTEGER,             -- Employee responsible for the sale (FK EmpRef added via ALTER TABLE later)
    FOREIGN KEY (ClntRef) REFERENCES Client_Registry(ClntId)
);

-- 16. Sales Order Line Items (Corrected for PostgreSQL)
CREATE TABLE Sales_Lines (
    SOLineId SERIAL PRIMARY KEY,      -- Use SERIAL for auto-incrementing PK in PostgreSQL
    SO_Ref INTEGER NOT NULL,         -- Link to the Sales Order Header (FK SO_Ref)
    PrdId INTEGER NOT NULL,          -- Product being ordered (FK PrdId)
    Qty INTEGER NOT NULL,            -- Quantity of this product ordered
    UnitPrc DECIMAL(12, 2),          -- Price per unit at the time of the order
    LineTot DECIMAL(14, 2),          -- Calculated line total (Qty * Price)
    FOREIGN KEY (SO_Ref) REFERENCES Sales_Hdrs(SO_Ref),
    FOREIGN KEY (PrdId) REFERENCES Prod_Catalog(PrdId)
);

-- 17. Linking Features to Products (Available Options - M:M Products <-> Features)
CREATE TABLE Prod_Feature_Avail (
    PrdId INTEGER NOT NULL,          -- Which Product Model (FK PrdId)
    FeatCd TEXT NOT NULL,            -- Which Feature Code (FK FeatCd)
    IsStdFlg BOOLEAN DEFAULT FALSE,  -- Is this feature standard on this model?
    OptPrc DECIMAL(8, 2),            -- Price if added as an option (may differ from standard cost)
    PRIMARY KEY (PrdId, FeatCd),
    FOREIGN KEY (PrdId) REFERENCES Prod_Catalog(PrdId),
    FOREIGN KEY (FeatCd) REFERENCES Prod_Features(FeatCd)
);

-- 18. Linking Features to Specific Vehicles (Installed Options - M:M Vehicles <-> Features)
CREATE TABLE Vehicle_Config (
    VINRef TEXT NOT NULL,            -- Which specific vehicle (FK VehVIN)
    FeatCd TEXT NOT NULL,            -- Which feature is installed (FK FeatCd)
    InstallTS TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When the feature was recorded/installed
    PRIMARY KEY (VINRef, FeatCd),
    FOREIGN KEY (VINRef) REFERENCES Vehicle_Inventory(VehVIN),
    FOREIGN KEY (FeatCd) REFERENCES Prod_Features(FeatCd)
);

-- 19. Service Records / Maintenance Log (Corrected for PostgreSQL)
CREATE TABLE Svc_Log (
    SvcTktId SERIAL PRIMARY KEY,      -- Use SERIAL for auto-incrementing PK in PostgreSQL
    VINRef TEXT NOT NULL,            -- VIN of the vehicle serviced (FK VehVIN)
    ClntRef INTEGER,                 -- Customer who brought it in (Nullable FK ClntId)
    SvcLocId TEXT NOT NULL,          -- Site Code where service was performed (FK LocId)
    TechRef INTEGER,                 -- Employee who performed the service (FK EmpRef added via ALTER TABLE later)
    SvcDt DATE NOT NULL,             -- Date of service
    SvcCd TEXT,                      -- e.g., 'OIL', 'WRNTY', 'REPAIR', 'INSP'
    SvcDesc TEXT,                    -- Details of work performed
    LbrHrs DECIMAL(5, 2),            -- Labor hours charged
    SvcCost DECIMAL(10, 2),          -- Total cost of the service event
    FOREIGN KEY (VINRef) REFERENCES Vehicle_Inventory(VehVIN),
    FOREIGN KEY (ClntRef) REFERENCES Client_Registry(ClntId),
    FOREIGN KEY (SvcLocId) REFERENCES Site_Directory(LocId)
);

-- 20. Parts Used in Service (M:M Service Records <-> Parts)
CREATE TABLE Svc_PartsUsed (
    SvcTktId INTEGER NOT NULL,       -- Link to the Service Log (FK SvcTktId)
    PrtId INTEGER NOT NULL,          -- Link to the Part Inventory (FK PrtSKU)
    Qty INTEGER NOT NULL,            -- Quantity of the part used
    CostBasis DECIMAL(10, 2),        -- Cost of the part when used in service
    PRIMARY KEY (SvcTktId, PrtId),
    FOREIGN KEY (SvcTktId) REFERENCES Svc_Log(SvcTktId),
    FOREIGN KEY (PrtId) REFERENCES Part_Inventory(PrtSKU)
);

-- 21. Lease Agreements (Simplified)
CREATE TABLE Lease_Contracts (
    LseId INTEGER PRIMARY KEY,       -- Changed back to INTEGER PK, assumed not auto-increment based on previous error report focusing only on others. If this also needs auto-increment, change to SERIAL PRIMARY KEY.
    VINRef TEXT NOT NULL UNIQUE,     -- VIN of the leased vehicle (FK VehVIN)
    ClntRef INTEGER NOT NULL,        -- Customer leasing the vehicle (FK ClntId)
    StartDt DATE NOT NULL,
    EndDt DATE NOT NULL,
    MnthPay DECIMAL(8, 2),
    LseStat TEXT DEFAULT 'ACTV',     -- e.g., 'ACTV', 'END', 'DFLT'
    FOREIGN KEY (VINRef) REFERENCES Vehicle_Inventory(VehVIN),
    FOREIGN KEY (ClntRef) REFERENCES Client_Registry(ClntId)
);

-- 22. Lease Payments / Installments (Corrected for PostgreSQL)
CREATE TABLE Lease_Installments (
    PmtId SERIAL PRIMARY KEY,        -- Use SERIAL for auto-incrementing PK in PostgreSQL
    LseRef INTEGER NOT NULL,         -- Link to the Lease Contract (FK LseId)
    PmtDt DATE NOT NULL,
    Amt DECIMAL(8, 2),
    PmtMeth TEXT,                    -- e.g., 'ACH', 'CC', 'CHK'
    FOREIGN KEY (LseRef) REFERENCES Lease_Contracts(LseId)
);

-- 23. Customer Loyalty Program Transactions (Corrected for PostgreSQL)
CREATE TABLE Loyalty_Ledger (
    TrnsId SERIAL PRIMARY KEY,       -- Use SERIAL for auto-incrementing PK in PostgreSQL
    ClntRef INTEGER NOT NULL,        -- Customer involved (FK ClntId)
    TrnsTyp TEXT NOT NULL,           -- 'EARN', 'REDEEM', 'ADJ'
    Pts INTEGER NOT NULL,            -- Points earned (+) or redeemed (-)
    TrnsTS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SORef INTEGER,                   -- Optional link to a Sales Order (FK SO_Ref)
    TrnsNotes TEXT,
    FOREIGN KEY (ClntRef) REFERENCES Client_Registry(ClntId),
    FOREIGN KEY (SORef) REFERENCES Sales_Hdrs(SO_Ref)
);

-- Bridge Table: Employee Skills (M:M between Personnel_Roster and Skill_Codes)
CREATE TABLE Employee_Skills (
    EmpRef INTEGER NOT NULL,         -- Reference to Personnel_Roster (FK EmpRef)
    SkllCd TEXT NOT NULL,            -- Reference to Skill_Codes (FK SkllCd)
    SkllLvl INTEGER,                 -- Optional: Proficiency level (e.g., 1-5)
    CertDt DATE,                     -- Optional: Date certification was achieved
    PRIMARY KEY (EmpRef, SkllCd),
    FOREIGN KEY (EmpRef) REFERENCES Personnel_Roster(EmpRef),
    FOREIGN KEY (SkllCd) REFERENCES Skill_Codes(SkllCd)
);

-- Bridge Table: Part Suppliers (M:M between Part_Inventory and Vendor_Master)
CREATE TABLE Part_Suppliers (
    PrtId INTEGER NOT NULL,          -- Reference to Part_Inventory (FK PrtSKU)
    VndrId INTEGER NOT NULL,         -- Reference to Vendor_Master (FK VndrId)
    VndrPrtNo TEXT,                  -- Supplier's specific part number for this item (Optional)
    LT_Days INTEGER,                 -- Typical lead time from this supplier for this part (Optional)
    SupCost DECIMAL(10, 2),          -- Cost when purchasing this part from this specific supplier
    PrefSupFlg BOOLEAN DEFAULT FALSE,-- Is this the preferred supplier for this part?
    PRIMARY KEY (PrtId, VndrId),
    FOREIGN KEY (PrtId) REFERENCES Part_Inventory(PrtSKU),
    FOREIGN KEY (VndrId) REFERENCES Vendor_Master(VndrId)
);

-- Bridge Table: Order Promotions Applied (M:M between Sales_Hdrs and Promo_Campaigns)
CREATE TABLE Applied_Order_Promos (
    SO_Ref INTEGER NOT NULL,         -- Reference to Sales_Hdrs (FK SO_Ref)
    PrmoCd TEXT NOT NULL,            -- Reference to Promo_Campaigns (FK PrmoCd)
    DscntAmt DECIMAL(10, 2),         -- The actual discount amount calculated for this order from this promo
    ApplyTS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (SO_Ref, PrmoCd),
    FOREIGN KEY (SO_Ref) REFERENCES Sales_Hdrs(SO_Ref),
    FOREIGN KEY (PrmoCd) REFERENCES Promo_Campaigns(PrmoCd)
);


-- Add Foreign Key constraints using ALTER TABLE for dependencies resolved after initial creation --

ALTER TABLE Org_Departments ADD CONSTRAINT fk_dept_mgr FOREIGN KEY (MgrRef) REFERENCES Personnel_Roster(EmpRef);
ALTER TABLE Sales_Hdrs ADD CONSTRAINT fk_sales_emp FOREIGN KEY (SalesRepRef) REFERENCES Personnel_Roster(EmpRef);
ALTER TABLE Svc_Log ADD CONSTRAINT fk_svc_tech FOREIGN KEY (TechRef) REFERENCES Personnel_Roster(EmpRef);


-- Consolidated Sample Data INSERT Script (Car Manufacturing - 23 Tables)
-- 5 Sample Rows per Table (where applicable)
-- Includes Complex Naming, M:M Relationships, Varied Data
-- Designed to correspond to the provided CREATE TABLE script.
-- ASSUMES TABLES ARE ALREADY CREATED CORRECTLY.
-- MUST BE RUN IN ORDER DUE TO FOREIGN KEY DEPENDENCIES.
-- NOTE: Explicit IDs used for SERIAL columns (e.g., AddrId starting at 1) for script consistency.

-- Group 1: Independent Masters --

INSERT INTO Site_Directory (LocId, LocName, LocType, LocCity, LocState) VALUES
('FAC01', 'Main Assembly Plant', 'FCTRY', 'Detroit', 'MI'),
('DLNY', 'Downtown Premier Auto', 'DLR', 'New York', 'NY'),
('SVCW', 'West Coast Service Hub', 'SVC', 'Los Angeles', 'CA'),
('WHSE-C', 'Central Distribution WH', 'WHSE', 'Chicago', 'IL'),
('HQ01', 'Corporate Headquarters', 'OFFC', 'Detroit', 'MI');

INSERT INTO Skill_Codes (SkllCd, SkllName, SkllCat) VALUES
('WLD-TIG', 'TIG Welding Steel', 'MFG'),
('DIAG-L3', 'Engine Diagnostics Level 3', 'DIAG'),
('CRM-EXP', 'CRM Platform Expert', 'SALES'),
('PNT-ROBO', 'Paint Booth Robotics Op', 'MFG'),
('FIN-AUDIT', 'Internal Financial Audit', 'FIN');

INSERT INTO Prod_Features (FeatCd, FeatName, FeatDesc, OptCost) VALUES
('SNRF-PAN', 'Panoramic Sunroof', 'Full glass sunroof, retractable', 1550.00),
('NAV-PR', 'Premium Navigation Package', '12-inch display, live traffic data', 1225.50),
('AWD', 'All-Wheel Drive', 'Enhanced traction ctrl sys', 2000.00),
('SEAT-V', 'Ventilated Leather Seats', 'Heated and Cooled front seating', 975.00),
('SND-PREM', 'High-Fidelity Sound System', '14-speaker premium audio by Harman', 750.00);

INSERT INTO Promo_Campaigns (PrmoCd, PrmoName, PrmoDesc, DscntType, DscntVal, StartDt, EndDt, ActiveFlg) VALUES
('SUM25', 'Summer Sale 2025', '% discount on select models', 'PERC', 5.00, '2025-06-01', '2025-08-31', TRUE),
('LOYALTY2', 'Loyalty Bonus Tier 2', '$ discount for repeat buyers > 1 prev purchase', 'FIXED', 500.00, '2025-01-01', '2025-12-31', TRUE),
('NYR25-FIN', 'New Year Finance Offer', 'Special APR or cash discount', 'PERC', 3.50, '2025-01-01', '2025-01-31', FALSE),
('SVC-1ST', 'First Service Discount', '$50 off first scheduled maint.', 'FIXED', 50.00, '2025-03-01', '2025-12-31', TRUE),
('CLEAR24', 'Model Year Clearance 24', 'Discount on remaining 2024 stock', 'PERC', 7.50, '2025-09-01', '2025-10-31', TRUE);

INSERT INTO Vendor_Master (VndrId, VName, POCName, POCEmail, VCity, VState) VALUES
(101, 'SteelWorks Inc.', 'John Smith', 'jsmith@steelworks.com', 'Pittsburgh', 'PA'),
(102, 'ElectroChip Ltd.', 'Maria Garcia', 'm.garcia@electrochip.co', 'San Jose', 'CA'),
(103, 'Global Tires Co.', 'Sam Chen', 'schen@globaltires.net', 'Akron', 'OH'),
(104, 'PlastiForm Solutions', NULL, 'sales@plastiform.com', 'Gary', 'IN'),
(105, 'Fine Finish Paints', 'Eva Rostova', 'eva.r@ffpaints.biz', 'Cleveland', 'OH');

-- Group 2: Core Masters --

INSERT INTO Org_Departments (DptCd, DptName, MgrRef) VALUES
('MFG', 'Manufacturing', NULL),
('SALES', 'Sales and Marketing', NULL),
('SVC-OPS', 'Service Operations', NULL),
('HR', 'Human Resources', NULL),
('FIN', 'Finance and Accounting', NULL);

INSERT INTO Prod_Catalog (PrdId, MdlNm, BodyStyleCd, BsMRP, LnchYr) VALUES
(1, 'Aurora', 'SDN', 35200.00, 2023),
(2, 'TundraMax', 'TRK', 48500.00, 2024),
(3, 'CityScape', 'SUV', 41450.99, 2023),
(4, 'Zephyr', 'SDN', 52100.00, 2025),
(5, 'Nomad XL', 'SUV', 46050.00, 2024);

INSERT INTO Part_Inventory (PrtSKU, PrtNm, PrtDtl, PrtCat, StdCost, MatSpec) VALUES
(1001, 'Engine Block V6 3.5L', '3.5L V6 Aluminum Block Assy', 'ENG', 1850.00, 'ALU-35X'),
(1002, 'Transmission Assy A8', '8-Speed Automatic FWD/AWD', 'TRN', 2550.00, 'ASM-A8-R2'),
(2001, 'ECU Mod XR3', 'Engine Control Unit Model XR3', 'ELEC', 675.50, 'ECU-XR3'),
(3001, 'Brake Pad Set - F', 'High-perf ceramic pads (Front)', 'CHAS', 125.00, 'CERAM-HPF'),
(4001, 'Windshield Glass Std', 'Std Laminated safety glass', 'BODY', 355.00, 'GLASS-LAM-STD'),
(5002, 'Steering Wheel Assy', 'Standard Steering Wheel w/ Airbag', 'CTRL', 180.00, 'PU-STL-AB'),
(6001, 'Headlight Assy - LED', 'LED Headlight Assembly - Left', 'ELEC', 450.00, 'LED-HL-L'),
(6002, 'Headlight Assy - LED', 'LED Headlight Assembly - Right', 'ELEC', 450.00, 'LED-HL-R'),
(7001, 'Fuel Pump Mod', 'In-tank fuel pump module', 'FUEL', 220.50, 'FP-MOD-IT'),
(8001, 'Seat Frame - Front', 'Standard front seat frame structure', 'BODY', 150.00, 'FRAME-SEATF');

INSERT INTO Client_Registry (ClntId, FstNm, LstNm, OrgNm, Email, Phone, RegDt) VALUES
(5001, 'Alice', 'Johnson', NULL, 'alice.j@email.com', '555-123-4567', '2024-01-15'),
(5002, 'Bob', 'Williams', 'BW Consulting', 'bob@bwconsulting.net', '555-987-6543', '2024-03-22'),
(5003, 'Charlie', 'Brown', NULL, 'cbrown@mailservice.org', NULL, '2024-05-10'),
(5004, 'Diana', 'Miller', 'Miller & Associates', 'diana.miller@millerassoc.com', '555-333-4444', '2024-08-01'),
(5005, 'Ethan', 'Davis', NULL, 'ethan.d@mymail.com', '555-555-5555', '2024-11-30');

-- Group 3: Personnel & Dependent Details --

-- Corrected INSERT statements for Personnel_Roster (using full PayType codes)
INSERT INTO Personnel_Roster (EmpRef, FName, LName, JobCd, DptRef, HireDate, PayType, PayAmt, CorpEmail, WorkPhone, WorkLocId, SupRef, IsActiveFlg) VALUES
(10101, 'Sarah', 'Chen', 'SALESMGR', 'SALES', '2020-05-15', 'SAL', 98000.00, 'sarah.chen@carco.com', '212-555-1001', 'DLNY', NULL, TRUE),
(10102, 'Mike', 'Davis', 'SALESREP', 'SALES', '2022-08-01', 'SAL', 64000.00, 'mike.davis@carco.com', '212-555-1002', 'DLNY', 10101, TRUE),
(20201, 'David', 'Lee', 'MECH-L3', 'SVC-OPS', '2019-11-01', 'HRLY', 36.75, 'david.lee@carco.com', '213-555-2001', 'SVCW', 20202, TRUE),
(20202, 'Maria', 'Garcia', 'SVCMGR', 'SVC-OPS', '2018-03-10', 'SAL', 91000.00, 'maria.garcia@carco.com', '213-555-2000', 'SVCW', NULL, TRUE),
(30305, 'Linda', 'Kim', 'ASMB-LEAD', 'MFG', '2017-06-01', 'HRLY', 32.00, 'linda.kim@carco.com', '313-555-3000', 'FAC01', NULL, TRUE);

-- NOTE: Explicit IDs (1-5) used for AddrId (SERIAL column) for script consistency.
INSERT INTO Client_Addresses (AddrId, ClntRef, AddrTyp, AddrLn1, City, StateProv, PostalCd) VALUES
(1, 5001, 'PRI', '123 Main St', 'Anytown', 'VA', '22030'),
(2, 5001, 'BIL', 'PO Box 456', 'Anytown', 'VA', '22030'),
(3, 5002, 'PRI', '456 Oak Ave, Ste 200', 'Metropolis', 'NY', '10001'),
(4, 5003, 'PRI', '789 Pine Ln', 'Smallville', 'KS', '66001'),
(5, 5004, 'WRK', '100 Business Blvd', 'Big City', 'TX', '75001');

-- Group 4: Vehicles --

-- Corrected INSERT for Vehicle_Inventory (Using ProdDate)

INSERT INTO Vehicle_Inventory (VehVIN, PrdId, ProdDate, CurrLocId, VehStat, ColorCd, ActlMSRP) VALUES
('VIN001', 1, '2024-11-01', 'FAC01', 'INV', 'BLK', 35200.00),
('VIN002', 2, '2024-11-15', 'FAC01', 'INV', 'RED', 48500.00),
('VIN003', 3, '2024-12-01', 'DLNY', 'SOLD', 'SIL', 41500.00),
('VIN004', 5, '2025-01-10', 'WHSE-C', 'INV', 'BLU', 46050.00),
('VIN005', 1, '2025-02-01', 'DLNY', 'LSED', 'WHT', 35500.00),
('VIN006', 2, '2025-02-10', 'WHSE-C', 'INV', 'GRY', 48600.00),
('VIN007', 4, '2025-02-15', 'FAC01', 'INV', 'BLK', 52100.00),
('VIN008', 5, '2025-02-20', 'SVCW', 'SVC', 'GRN', 46100.00),
('VIN009', 1, '2025-03-01', 'DLNY', 'INV', 'RED', 35300.00),
('VIN010', 3, '2025-03-05', 'WHSE-C', 'INV', 'WHT', 41550.00);

-- Group 5: Product/Vehicle Configs --

INSERT INTO Prod_BOM (PrdId, PrtId, QtyPerAssy) VALUES
(1, 1001, 1), (1, 2001, 1), (1, 3001, 2), (1, 4001, 1), (1, 5002, 1),
(2, 1001, 1), (2, 1002, 1), (2, 6001, 1), (2, 6002, 1), (2, 7001, 1),
(3, 2001, 1), (3, 4001, 1), (3, 5002, 1), (3, 7001, 1), (3, 8001, 2),
(4, 1001, 1), (4, 1002, 1), (4, 5002, 1), (4, 8001, 2), (4, 2001, 1),
(5, 1001, 1), (5, 7001, 1), (5, 8001, 2), (5, 6001, 1), (5, 6002, 1);

INSERT INTO Prod_Feature_Avail (PrdId, FeatCd, IsStdFlg, OptPrc) VALUES
(1, 'NAV-PR', FALSE, 1225.50), (1, 'SNRF-PAN', FALSE, 1550.00), (1, 'AWD', FALSE, 2000.00),
(2, 'AWD', TRUE, 0.00), (2, 'SND-PREM', FALSE, 800.00),
(3, 'SNRF-PAN', FALSE, 1600.00), (3, 'SEAT-V', FALSE, 975.00),
(4, 'NAV-PR', TRUE, 0.00), (4, 'SEAT-V', FALSE, 975.00), (4, 'SND-PREM', TRUE, 0.00),
(5, 'AWD', TRUE, 0.00), (5, 'NAV-PR', TRUE, 0.00), (5, 'SNRF-PAN', FALSE, 1500.00);

INSERT INTO Vehicle_Config (VINRef, FeatCd, InstallTS) VALUES
('VIN001', 'NAV-PR', '2024-11-01 08:00:00'),
('VIN003', 'SNRF-PAN', '2024-12-01 09:00:00'),
('VIN003', 'NAV-PR', '2024-12-01 09:00:00'),
('VIN005', 'SEAT-V', '2025-02-01 10:00:00'),
('VIN005', 'SND-PREM', '2025-02-01 10:00:00');

-- Group 6: Part Sourcing/Skills --

INSERT INTO Part_Suppliers (PrtId, VndrId, VndrPrtNo, LT_Days, SupCost, PrefSupFlg) VALUES
(1001, 101, 'SW-ENGBLK-V6', 15, 1750.00, TRUE),
(1002, 101, 'SW-TRN-A8', 25, 2500.00, TRUE),
(2001, 102, 'EC-XR3-MOD', 10, 640.00, TRUE),
(3001, 105, 'FFP-BRKPAD-CER', 5, 118.00, TRUE),
(4001, 104, 'PF-WSHLD-STD', 12, 340.00, TRUE);

INSERT INTO Employee_Skills (EmpRef, SkllCd, SkllLvl, CertDt) VALUES
(10101, 'CRM-EXP', 5, '2022-01-10'),
(20201, 'DIAG-L3', 3, '2023-06-15'),
(20202, 'FIN-AUDIT', 1, NULL), -- Changed skill for variety
(30305, 'WLD-TIG', 3, '2021-05-20'),
(30305, 'PNT-ROBO', 2, NULL); -- Linda Kim has two skills

-- Group 7: Sales --

-- Corrected INSERT for Sales_Hdrs (Using 'CANC' instead of 'CANCEL')

INSERT INTO Sales_Hdrs (SO_Ref, ClntRef, OrdTS, OrdStat, OrdTotal, SalesRepRef) VALUES
(9001, 5001, '2025-04-15 10:30:00', 'SHIP', 77000.00, 10102),
(9002, 5003, '2025-04-20 14:00:00', 'PLACED', 46050.00, 10102),
(9003, 5002, '2025-04-22 09:15:00', 'PROC', 100600.00, 10101),
(9004, 5001, '2025-04-28 11:00:00', 'PLACED', NULL, 10102),
(9005, 5005, '2025-05-01 16:00:00', 'CANC', NULL, 10101); -- Corrected value 'CANC'

-- NOTE: Explicit IDs (1-5) used for SOLineId (SERIAL column) for script consistency.
INSERT INTO Sales_Lines (SOLineId, SO_Ref, PrdId, Qty, UnitPrc, LineTot) VALUES
(1, 9001, 1, 1, 35200.00, 35200.00),
(2, 9001, 3, 1, 41800.00, 41800.00),
(3, 9002, 5, 1, 46050.00, 46050.00),
(4, 9003, 2, 1, 48500.00, 48500.00),
(5, 9003, 4, 1, 52100.00, 52100.00);

INSERT INTO Applied_Order_Promos (SO_Ref, PrmoCd, DscntAmt, ApplyTS) VALUES
(9001, 'LOYALTY2', 500.00, '2025-04-15 10:31:00'),
(9003, 'SUM25', 5030.00, '2025-04-22 09:16:00'),
(9004, 'LOYALTY2', 500.00, '2025-04-28 11:01:00'),
(9002, 'SVC-1ST', 50.00, '2025-04-20 14:01:00'),
(9001, 'SVC-1ST', 50.00, '2025-04-15 10:31:30');

-- Group 8: Service --

-- NOTE: Explicit IDs (1-10) used for SvcTktId (SERIAL column) for script consistency.
INSERT INTO Svc_Log (SvcTktId, VINRef, ClntRef, SvcLocId, TechRef, SvcDt, SvcCd, SvcDesc, LbrHrs, SvcCost) VALUES
(1, 'VIN003', 5003, 'DLNY', 20201, '2025-03-10', 'WRNTY', 'Replaced faulty ECU under warranty claim #W8765', 2.5, 0.00),
(2, 'VIN005', 5005, 'DLNY', NULL, '2025-04-01', 'PM-A', 'Scheduled Maintenance Package A (Oil, Filter, Rotate).', 1.5, 175.50),
(3, 'VIN001', NULL, 'FAC01', 20201, '2025-01-15', 'QC-CHK', 'Post-production quality check', 1.0, 0.00),
(4, 'VIN003', 5003, 'DLNY', 20201, '2025-04-20', 'RP-BRK', 'Replaced front brake pads, customer pay.', 1.8, 380.00),
(5, 'VIN005', 5005, 'DLNY', 20201, '2025-04-25', 'DIAG', 'Check engine light diagnosis. Code P0300.', 0.5, 75.00),
(6, 'VIN006', 5001, 'SVCW', 20201, '2025-05-10', 'DIAG', 'Check light - reprogrammed headlight module', 1.0, 150.00),
(7, 'VIN008', NULL, 'SVCW', 20201, '2025-05-12', 'RP-FUEL', 'Replaced fuel pump, internal service order.', 2.2, 480.00),
(8, 'VIN010', 5003, 'SVCW', 20202, '2025-05-14', 'RP-BRK', 'Customer states grinding noise - replaced rear pads', 2.0, 410.00),
(9, 'VIN001', 5001, 'SVCW', 20201, '2025-05-18', 'OIL', 'Standard oil change service', 0.8, 95.00),
(10, 'VIN006', 5001, 'SVCW', 20202, '2025-05-20', 'WRNTY', 'Software update campaign #C2025-03 performed', 0.5, 0.00);

-- Group 9: Service Details --

INSERT INTO Svc_PartsUsed (SvcTktId, PrtId, Qty, CostBasis) VALUES
(1, 2001, 1, 675.50), -- SvcTktId 1 used Part 2001
(4, 3001, 1, 125.00), -- SvcTktId 4 used Part 3001
(6, 6001, 1, 450.00), -- SvcTktId 6 used Part 6001
(7, 7001, 1, 220.50), -- SvcTktId 7 used Part 7001
(8, 3001, 1, 130.00); -- SvcTktId 8 used Part 3001

-- Group 10: Leasing --

INSERT INTO Lease_Contracts (LseId, VINRef, ClntRef, StartDt, EndDt, MnthPay, LseStat) VALUES
(1001, 'VIN005', 5005, '2025-02-15', '2028-02-14', 550.00, 'ACTV'),
(1002, 'VIN006', 5001, '2025-03-01', '2028-02-29', 620.00, 'ACTV'),
(1003, 'VIN007', 5002, '2025-03-10', '2027-03-09', 680.00, 'ACTV'),
(1004, 'VIN009', 5004, '2025-04-01', '2028-03-31', 510.00, 'ACTV'),
(1005, 'VIN010', 5003, '2025-04-05', '2026-04-04', 590.00, 'END');

-- Group 11: Lease Payments --

-- NOTE: Explicit IDs (1-5) used for PmtId (SERIAL column) for script consistency.
INSERT INTO Lease_Installments (PmtId, LseRef, PmtDt, Amt, PmtMeth) VALUES
(1, 1001, '2025-03-15', 550.00, 'ACH'),
(2, 1001, '2025-04-15', 550.00, 'ACH'),
(3, 1001, '2025-05-15', 550.00, 'ACH'),
(4, 1002, '2025-04-01', 620.00, 'CC'),
(5, 1002, '2025-05-01', 620.00, 'CC');

-- Group 12: Loyalty --

-- NOTE: Explicit IDs (1-5) used for TrnsId (SERIAL column) for script consistency.
INSERT INTO Loyalty_Ledger (TrnsId, ClntRef, TrnsTyp, Pts, TrnsTS, SORef, TrnsNotes) VALUES
(1, 5001, 'EARN', 1000, '2025-04-15 10:32:00', 9001, 'Points earned from SO 9001'),
(2, 5002, 'EARN', 1500, '2025-04-22 09:17:00', 9003, 'Points earned from SO 9003'),
(3, 5001, 'REDEEM', -250, '2025-04-28 11:02:00', 9004, 'Points redeemed against SO 9004'),
(4, 5003, 'ADJ', 50, '2025-05-01 10:00:00', NULL, 'Manual adjustment - customer service'),
(5, 5005, 'EARN', 0, '2025-05-01 16:05:00', 9005, 'Earn reversed - SO 9005 cancelled.');

-- Group 13: Mfg_WorkOrders -- (Aiming for 5 rows)
INSERT INTO Mfg_WorkOrders (WO_Ref, TgtPrd, BuildQty, IssDt, EstCompDt, WO_Stat) VALUES
(101, 1, 50, '2025-05-01', '2025-05-15', 'PEND'),
(102, 2, 30, '2025-05-01', '2025-05-20', 'PEND'),
(103, 4, 25, '2025-05-05', '2025-05-25', 'INPR'),
(104, 5, 40, '2025-05-10', '2025-06-05', 'PEND'),
(105, 1, 10, '2025-05-12', '2025-05-18', 'COMP');

-- Group 14: Updates for FKs (Run AFTER all inserts) --

UPDATE Org_Departments SET MgrRef = 10101 WHERE DptCd = 'SALES';
UPDATE Org_Departments SET MgrRef = 20202 WHERE DptCd = 'SVC-OPS';
UPDATE Org_Departments SET MgrRef = NULL WHERE DptCd IN ('MFG', 'HR', 'FIN'); -- Set others explicitly to NULL if no manager defined

UPDATE Sales_Hdrs SET SalesRepRef = 10102 WHERE SO_Ref IN (9001, 9002, 9004);
UPDATE Sales_Hdrs SET SalesRepRef = 10101 WHERE SO_Ref IN (9003, 9005);

UPDATE Svc_Log SET TechRef = 20201 WHERE SvcTktId IN (1, 3, 4, 5, 6, 7, 9);
UPDATE Svc_Log SET TechRef = 20202 WHERE SvcTktId IN (8, 10);
UPDATE Svc_Log SET TechRef = NULL WHERE SvcTktId = 2;