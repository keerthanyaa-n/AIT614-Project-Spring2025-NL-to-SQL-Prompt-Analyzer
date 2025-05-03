
-- 1. Addresses Table (Created first because it's referenced by other tables)

CREATE TABLE Addresses (
    AddressID SERIAL PRIMARY KEY,
    StreetAddress TEXT NOT NULL,
    City TEXT NOT NULL,
    State TEXT NOT NULL,
    ZipCode TEXT NOT NULL,
    Country TEXT DEFAULT 'USA',
    AddressType TEXT -- ('Primary', 'Shipping', 'Billing', 'Home', 'Work', 'Site')
);

-- 2. Products Table
CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    ModelName TEXT NOT NULL,
    BodyStyle TEXT NOT NULL,
    BasePrice DECIMAL(10, 2) NOT NULL,
    LaunchYear INTEGER NOT NULL,
    IsActive BOOLEAN NOT NULL
);

-- 3. Features Table
CREATE TABLE Features (
    FeatureID SERIAL PRIMARY KEY,
    FeatureName TEXT NOT NULL,
    FeatureType TEXT NOT NULL,
    AdditionalCost DECIMAL(10, 2) NOT NULL
);


-- 4. ProductFeatures Table (Linking Table)
CREATE TABLE ProductFeatures (
    ProductID INTEGER,
    FeatureID INTEGER,
    PRIMARY KEY (ProductID, FeatureID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (FeatureID) REFERENCES Features(FeatureID) ON DELETE CASCADE
);

-- 5. Suppliers Table
CREATE TABLE Suppliers (
    SupplierID SERIAL PRIMARY KEY,
    SupplierName TEXT NOT NULL,
    ContactPerson TEXT,
    ContactEmail TEXT,
    PrimaryAddressID INTEGER,
    FOREIGN KEY (PrimaryAddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

-- 6. Components Table
CREATE TABLE Components (
    ComponentID SERIAL PRIMARY KEY,
    ComponentName TEXT NOT NULL,
    Description TEXT,
    Category TEXT NOT NULL,
    UnitCost DECIMAL(10, 2) NOT NULL,
    Material TEXT,
    SupplierID INTEGER,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL
);

-- 7. ProductComponents Table (Linking Table)
CREATE TABLE ProductComponents (
    ProductID INTEGER,
    ComponentID INTEGER,
    QuantityRequired INTEGER NOT NULL,
    PRIMARY KEY (ProductID, ComponentID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (ComponentID) REFERENCES Components(ComponentID) ON DELETE CASCADE
);

-- 8. Locations Table
CREATE TABLE Locations (
    LocationID SERIAL PRIMARY KEY,
    LocationName TEXT NOT NULL,
    LocationType TEXT NOT NULL, -- ('Factory', 'Dealership', 'Office', 'Warehouse', 'Service Center')
    PrimaryAddressID INTEGER,
    FOREIGN KEY (PrimaryAddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

-- 9. Departments Table (requires circular reference handling)
CREATE TABLE Departments (
    DepartmentID SERIAL PRIMARY KEY,
    DepartmentName TEXT NOT NULL,
    ManagerID INTEGER -- Will be linked to Employees.EmployeeID later
);

-- 10. Employees Table
CREATE TABLE Employees (
    EmployeeID SERIAL PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    JobTitle TEXT NOT NULL,
    DepartmentID INTEGER,
    HireDate DATE NOT NULL,
    TerminationDate DATE,
    Status TEXT NOT NULL, -- ('Active', 'Terminated', 'On Leave')
    SalaryOrRate DECIMAL(10, 2) NOT NULL,
    PayType TEXT NOT NULL, -- ('Salary', 'Hourly')
    Email TEXT,
    WorkPhone TEXT,
    LocationID INTEGER,
    HomeAddressID INTEGER,
    SupervisorID INTEGER,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID) ON DELETE SET NULL,
    FOREIGN KEY (LocationID) REFERENCES Locations(LocationID) ON DELETE SET NULL,
    FOREIGN KEY (HomeAddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL,
    FOREIGN KEY (SupervisorID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL
);

-- Add foreign key to Departments after Employees is created
ALTER TABLE Departments
ADD CONSTRAINT fk_departments_manager
FOREIGN KEY (ManagerID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL;

-- 11. WorkOrders Table
CREATE TABLE WorkOrders (
    WorkOrderID SERIAL PRIMARY KEY,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    DateCreated DATE NOT NULL,
    DueDate DATE,
    Status TEXT NOT NULL, -- ('Pending', 'In Progress', 'Completed', 'Cancelled')
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT
);

-- 12. Customers Table
CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    CompanyName TEXT,
    Email TEXT,
    Phone TEXT,
    PrimaryAddressID INTEGER,
    RegistrationDate DATE NOT NULL,
    LoyaltyPointsBalance INTEGER DEFAULT 0,
    FOREIGN KEY (PrimaryAddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

-- 13. Vehicles Table
CREATE TABLE Vehicles (
    VehicleID SERIAL PRIMARY KEY,
    VIN TEXT UNIQUE NOT NULL,
    ProductID INTEGER NOT NULL,
    ManufactureDate DATE NOT NULL,
    Color TEXT,
    WorkOrderID INTEGER,
    CurrentMileage INTEGER,
    LastServiceDate DATE,
    CurrentStatus TEXT NOT NULL, -- ('Inventory', 'Sold', 'Leased', 'Rented', 'In Service', 'Decommissioned')
    CurrentHolderCustomerID INTEGER,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT,
    FOREIGN KEY (WorkOrderID) REFERENCES WorkOrders(WorkOrderID) ON DELETE SET NULL,
    FOREIGN KEY (CurrentHolderCustomerID) REFERENCES Customers(CustomerID) ON DELETE SET NULL
);

-- 14. VehicleFeatures Table (Linking Table)
CREATE TABLE VehicleFeatures (
    VehicleID INTEGER,
    FeatureID INTEGER,
    PRIMARY KEY (VehicleID, FeatureID),
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID) ON DELETE CASCADE,
    FOREIGN KEY (FeatureID) REFERENCES Features(FeatureID) ON DELETE CASCADE
);

-- 15. SalesOrders Table
CREATE TABLE SalesOrders (
    SalesOrderID SERIAL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    OrderTimestamp TIMESTAMP NOT NULL,
    ShippingAddressID INTEGER,
    Status TEXT NOT NULL, -- ('Placed', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
    TotalAmount DECIMAL(10, 2),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (ShippingAddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

-- 16. SalesOrderItems Table
CREATE TABLE SalesOrderItems (
    OrderItemID SERIAL PRIMARY KEY,
    SalesOrderID INTEGER NOT NULL,
    VehicleID INTEGER,
    Quantity INTEGER NOT NULL,
    AgreedPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (SalesOrderID) REFERENCES SalesOrders(SalesOrderID) ON DELETE CASCADE,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID) ON DELETE SET NULL
);

-- 17. LeaseRentalAgreements Table
CREATE TABLE LeaseRentalAgreements (
    AgreementID SERIAL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    VehicleID INTEGER NOT NULL,
    AgreementType TEXT NOT NULL, -- ('Lease', 'Rental')
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    MonthlyPayment DECIMAL(10, 2),
    RentalRatePerDay DECIMAL(10, 2),
    Status TEXT NOT NULL, -- ('Active', 'Completed', 'Terminated Early', 'Pending')
    Notes TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID) ON DELETE RESTRICT
);

-- 18. ServiceRecords Table
CREATE TABLE ServiceRecords (
    ServiceID SERIAL PRIMARY KEY,
    VehicleID INTEGER NOT NULL,
    CustomerID INTEGER NOT NULL,
    LocationID INTEGER NOT NULL,
    TechnicianID INTEGER,
    ServiceDate DATE NOT NULL,
    ServiceType TEXT NOT NULL,
    IsWarrantyClaim BOOLEAN NOT NULL,
    Notes TEXT,
    LaborHours DECIMAL(5, 2),
    PartsCost DECIMAL(10, 2),
    LaborCost DECIMAL(10, 2),
    TotalCost DECIMAL(10, 2),
    PointsEarned INTEGER,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID) ON DELETE RESTRICT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (LocationID) REFERENCES Locations(LocationID) ON DELETE RESTRICT,
    FOREIGN KEY (TechnicianID) REFERENCES Employees(EmployeeID) ON DELETE SET NULL
);

-- 19. ServicePartsUsed Table (Linking Table)
CREATE TABLE ServicePartsUsed (
    ServiceID INTEGER,
    ComponentID INTEGER,
    QuantityUsed INTEGER NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (ServiceID, ComponentID),
    FOREIGN KEY (ServiceID) REFERENCES ServiceRecords(ServiceID) ON DELETE CASCADE,
    FOREIGN KEY (ComponentID) REFERENCES Components(ComponentID) ON DELETE RESTRICT
);

-- 20. LoyaltyTransactions Table
CREATE TABLE LoyaltyTransactions (
    TransactionID SERIAL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    TransactionType TEXT NOT NULL, -- ('Earned', 'Redeemed', 'Adjustment', 'Expired')
    PointsChanged INTEGER NOT NULL,
    TransactionDate TIMESTAMP NOT NULL,
    RelatedServiceID INTEGER,
    RelatedAgreementID INTEGER,
    Notes TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (RelatedServiceID) REFERENCES ServiceRecords(ServiceID) ON DELETE SET NULL,
    FOREIGN KEY (RelatedAgreementID) REFERENCES LeaseRentalAgreements(AgreementID) ON DELETE SET NULL
);

-- 21. InventoryLevels Table
CREATE TABLE InventoryLevels (
    InventoryID SERIAL PRIMARY KEY,
    LocationID INTEGER NOT NULL,
    ProductID INTEGER,
    ComponentID INTEGER,
    QuantityOnHand INTEGER NOT NULL,
    LastUpdated TIMESTAMP NOT NULL,
    FOREIGN KEY (LocationID) REFERENCES Locations(LocationID) ON DELETE RESTRICT,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (ComponentID) REFERENCES Components(ComponentID) ON DELETE CASCADE,
    CONSTRAINT check_product_or_component CHECK (
        (ProductID IS NULL AND ComponentID IS NOT NULL) OR 
        (ProductID IS NOT NULL AND ComponentID IS NULL)
    )
);

-- addresses are given below 

INSERT INTO Addresses (StreetAddress, City, State, ZipCode, Country, AddressType) VALUES
-- Corporate & Manufacturing Sites
('1000 Manufacturing Way', 'Detroit', 'MI', '48201', 'USA', 'Site'),
('2500 Assembly Drive', 'Toledo', 'OH', '43604', 'USA', 'Site'),
('800 Industrial Parkway', 'Arlington', 'TX', '76010', 'USA', 'Site'),

-- Corporate Offices
('555 Headquarters Plaza', 'Chicago', 'IL', '60601', 'USA', 'Work'),
('100 Corporate Drive', 'Atlanta', 'GA', '30301', 'USA', 'Work'),
('2100 Business Center Blvd', 'Boston', 'MA', '02110', 'USA', 'Work'),

-- Dealerships & Service Centers
('789 Auto Mall Road', 'Los Angeles', 'CA', '90001', 'USA', 'Site'),
('456 Dealership Drive', 'Miami', 'FL', '33101', 'USA', 'Site'),
('234 Service Center Ave', 'Phoenix', 'AZ', '85001', 'USA', 'Site'),

-- Employee Residences
('123 Oak Street', 'Seattle', 'WA', '98101', 'USA', 'Home'),
('456 Maple Avenue', 'Portland', 'OR', '97201', 'USA', 'Home'),
('789 Pine Road', 'Denver', 'CO', '80201', 'USA', 'Home'),
('321 Cedar Lane', 'Austin', 'TX', '78701', 'USA', 'Home'),
('654 Birch Street', 'San Diego', 'CA', '92101', 'USA', 'Home'),

-- Customer Primary Addresses
('987 Residential Blvd', 'Nashville', 'TN', '37201', 'USA', 'Primary'),
('654 Highland Drive', 'Houston', 'TX', '77001', 'USA', 'Primary'),
('321 Valley View Road', 'Las Vegas', 'NV', '89101', 'USA', 'Primary'),
('147 Mountain Way', 'Salt Lake City', 'UT', '84101', 'USA', 'Primary'),
('258 Lake Drive', 'Minneapolis', 'MN', '55401', 'USA', 'Primary'),

-- Shipping Addresses
('369 Commerce Park', 'Philadelphia', 'PA', '19101', 'USA', 'Shipping'),
('741 Distribution Center', 'Cleveland', 'OH', '44101', 'USA', 'Shipping'),
('852 Logistics Way', 'Kansas City', 'MO', '64101', 'USA', 'Shipping'),

-- Billing Addresses
('963 Financial Plaza', 'New York', 'NY', '10001', 'USA', 'Billing'),
('159 Accounting Lane', 'San Francisco', 'CA', '94101', 'USA', 'Billing'),
('753 Invoice Road', 'Washington', 'DC', '20001', 'USA', 'Billing'),

-- Mixed Use Addresses
('951 Multipurpose Drive', 'Sacramento', 'CA', '95814', 'USA', 'Primary'),
('357 Business Park', 'Raleigh', 'NC', '27601', 'USA', 'Work'),
('159 Industrial Circle', 'Indianapolis', 'IN', '46201', 'USA', 'Site'),

-- Additional Employee Homes
('753 Suburban Lane', 'Charlotte', 'NC', '28201', 'USA', 'Home'),
('951 Country Road', 'St. Louis', 'MO', '63101', 'USA', 'Home'),
('357 City Avenue', 'Pittsburgh', 'PA', '15201', 'USA', 'Home'),

-- Additional Customer Addresses
('486 Residential Street', 'Orlando', 'FL', '32801', 'USA', 'Primary'),
('159 Neighborhood Lane', 'Dallas', 'TX', '75201', 'USA', 'Primary'),
('753 Community Road', 'San Antonio', 'TX', '78201', 'USA', 'Primary'),

-- International Addresses
('842 Queen Street', 'Toronto', 'ON', 'M5H 2N2', 'Canada', 'Primary'),
('15 Mexico City Blvd', 'Mexico City', 'CDMX', '11529', 'Mexico', 'Primary'),

-- Additional Service Centers
('951 Repair Road', 'Cincinnati', 'OH', '45201', 'USA', 'Site'),
('357 Maintenance Drive', 'Milwaukee', 'WI', '53201', 'USA', 'Site'),
('159 Service Street', 'Oklahoma City', 'OK', '73101', 'USA', 'Site'),

-- Additional Corporate Locations
('753 Executive Drive', 'Hartford', 'CT', '06101', 'USA', 'Work'),
('951 Manager Lane', 'Richmond', 'VA', '23218', 'USA', 'Work'),
('357 Admin Road', 'Providence', 'RI', '02901', 'USA', 'Work'),

-- Warehouse Locations
('159 Storage Drive', 'Memphis', 'TN', '38101', 'USA', 'Site'),
('753 Warehouse Road', 'Louisville', 'KY', '40201', 'USA', 'Site'),
('951 Inventory Lane', 'Jacksonville', 'FL', '32201', 'USA', 'Site'),

-- Additional Customer Shipping Addresses
('357 Delivery Way', 'Albuquerque', 'NM', '87101', 'USA', 'Shipping'),
('159 Reception Road', 'Tucson', 'AZ', '85701', 'USA', 'Shipping'),
('753 Shipment Street', 'Fresno', 'CA', '93721', 'USA', 'Shipping'),

-- Additional Mixed Use
('951 Multi-Use Center', 'Honolulu', 'HI', '96801', 'USA', 'Primary'),
('357 Flexible Space', 'Anchorage', 'AK', '99501', 'USA', 'Work'),
('159 Hybrid Location', 'Baltimore', 'MD', '21201', 'USA', 'Site'),
('753 Dual Purpose', 'Columbus', 'OH', '43215', 'USA', 'Primary');

-- the feataures are below 

INSERT INTO Features (FeatureName, FeatureType, AdditionalCost) VALUES
-- Safety Features
('Advanced Driver Assistance System', 'Safety', 2500.00),
('360-Degree Camera System', 'Safety', 1800.00),
('Lane Departure Warning', 'Safety', 895.00),
('Blind Spot Detection', 'Safety', 795.00),
('Automatic Emergency Braking', 'Safety', 1200.00),
('Adaptive Cruise Control', 'Safety', 1500.00),
('Night Vision Assistant', 'Safety', 2200.00),
('Parking Sensors', 'Safety', 600.00),
('Cross Traffic Alert', 'Safety', 750.00),
('Driver Drowsiness Detection', 'Safety', 850.00),

-- Interior Comfort
('Premium Leather Seats', 'Interior', 3500.00),
('Heated Front Seats', 'Interior', 850.00),
('Ventilated Seats', 'Interior', 1200.00),
('Massage Seats', 'Interior', 2000.00),
('Panoramic Sunroof', 'Interior', 1500.00),
('Ambient Lighting Package', 'Interior', 500.00),
('Four-Zone Climate Control', 'Interior', 1200.00),
('Premium Sound System', 'Interior', 2500.00),
('Wireless Phone Charging', 'Interior', 300.00),
('Head-Up Display', 'Interior', 1000.00),

-- Exterior Features
('20-inch Alloy Wheels', 'Exterior', 1200.00),
('LED Matrix Headlights', 'Exterior', 1800.00),
('Power Folding Mirrors', 'Exterior', 450.00),
('Roof Rails', 'Exterior', 400.00),
('Metallic Paint', 'Exterior', 695.00),
('Panoramic Glass Roof', 'Exterior', 1600.00),
('Adaptive Headlights', 'Exterior', 1200.00),
('Running Boards', 'Exterior', 850.00),
('Sport Body Kit', 'Exterior', 2500.00),
('Chrome Package', 'Exterior', 800.00),

-- Performance
('Sport Suspension', 'Performance', 1800.00),
('Performance Brakes', 'Performance', 2500.00),
('Sport Exhaust System', 'Performance', 1500.00),
('All-Wheel Drive', 'Performance', 2000.00),
('Adaptive Air Suspension', 'Performance', 2800.00),
('Sport Differential', 'Performance', 1850.00),
('Performance Tires', 'Performance', 1200.00),
('Engine Power Upgrade', 'Performance', 3500.00),
('Sport Steering', 'Performance', 950.00),
('Launch Control', 'Performance', 1500.00),

-- Technology
('Navigation System Plus', 'Technology', 1500.00),
('Premium Infotainment System', 'Technology', 2000.00),
('Digital Instrument Cluster', 'Technology', 1200.00),
('Rear Entertainment System', 'Technology', 2500.00),
('Voice Control System', 'Technology', 500.00),
('Smartphone Integration Package', 'Technology', 450.00),
('WiFi Hotspot', 'Technology', 300.00),
('Remote Start System', 'Technology', 650.00),
('Digital Key', 'Technology', 400.00),
('Advanced Parking Assistant', 'Technology', 1200.00);

-- product 

INSERT INTO Products (ModelName, BodyStyle, BasePrice, LaunchYear, IsActive) VALUES
-- Sedans
('Velocity S1', 'Sedan', 32500.00, 2022, true),
('Velocity S2 Sport', 'Sedan', 45000.00, 2023, true),
('Velocity S3 Luxury', 'Sedan', 58000.00, 2024, true),
('Velocity S4 Executive', 'Sedan', 72000.00, 2024, true),
('Velocity S2 Classic', 'Sedan', 38000.00, 2020, false),
('Velocity S1 Eco', 'Sedan', 29900.00, 2023, true),
('Velocity S3 Plus', 'Sedan', 62000.00, 2024, true),
('Velocity S4 Premium', 'Sedan', 78000.00, 2025, true),
('Velocity S2 Hybrid', 'Sedan', 42000.00, 2023, true),
('Velocity S1 Sport', 'Sedan', 35000.00, 2022, true),

-- SUVs
('Atlas X1', 'SUV', 38000.00, 2022, true),
('Atlas X2 Premium', 'SUV', 48000.00, 2023, true),
('Atlas X3 Luxury', 'SUV', 65000.00, 2024, true),
('Atlas X4 Elite', 'SUV', 82000.00, 2024, true),
('Atlas X1 Classic', 'SUV', 35000.00, 2020, false),
('Atlas X2 Sport', 'SUV', 52000.00, 2023, true),
('Atlas X3 Plus', 'SUV', 68000.00, 2024, true),
('Atlas X4 Ultimate', 'SUV', 88000.00, 2025, true),
('Atlas X2 Hybrid', 'SUV', 54000.00, 2023, true),
('Atlas X1 Adventure', 'SUV', 42000.00, 2022, true),

-- Crossovers
('Horizon C1', 'Crossover', 34000.00, 2022, true),
('Horizon C2 Plus', 'Crossover', 42000.00, 2023, true),
('Horizon C3 Premium', 'Crossover', 52000.00, 2024, true),
('Horizon C1 Sport', 'Crossover', 36000.00, 2023, true),
('Horizon C2 Classic', 'Crossover', 39000.00, 2021, false),
('Horizon C3 Hybrid', 'Crossover', 54000.00, 2024, true),
('Horizon C2 Adventure', 'Crossover', 44000.00, 2023, true),
('Horizon C1 Eco', 'Crossover', 32000.00, 2022, true),
('Horizon C3 Elite', 'Crossover', 56000.00, 2024, true),
('Horizon C2 Urban', 'Crossover', 43000.00, 2023, true),

-- Trucks
('Titan T1', 'Truck', 42000.00, 2022, true),
('Titan T2 Pro', 'Truck', 52000.00, 2023, true),
('Titan T3 Heavy', 'Truck', 65000.00, 2024, true),
('Titan T1 Work', 'Truck', 38000.00, 2022, true),
('Titan T2 Classic', 'Truck', 48000.00, 2020, false),
('Titan T3 Max', 'Truck', 68000.00, 2024, true),
('Titan T2 Sport', 'Truck', 54000.00, 2023, true),
('Titan T1 Plus', 'Truck', 44000.00, 2022, true),
('Titan T3 Ultimate', 'Truck', 72000.00, 2024, true),
('Titan T2 Limited', 'Truck', 58000.00, 2023, true),

-- Electric Vehicles
('Spark E1', 'Electric', 45000.00, 2023, true),
('Spark E2 Plus', 'Electric', 55000.00, 2024, true),
('Spark E3 Premium', 'Electric', 72000.00, 2024, true),
('Spark E1 Sport', 'Electric', 48000.00, 2023, true),
('Spark E2 Classic', 'Electric', 52000.00, 2022, false),
('Spark E3 Luxury', 'Electric', 78000.00, 2024, true),
('Spark E2 Long Range', 'Electric', 58000.00, 2024, true),
('Spark E1 Standard', 'Electric', 42000.00, 2023, true),
('Spark E3 Performance', 'Electric', 82000.00, 2025, true),
('Spark E2 Urban', 'Electric', 54000.00, 2024, true);

--

INSERT INTO Locations (LocationName, LocationType, PrimaryAddressID) VALUES
-- Manufacturing Factories
('Detroit Main Factory', 'Factory', 105),
('Toledo Assembly Plant', 'Factory', 106),
('Arlington Production Facility', 'Factory', 107),

-- Corporate Offices
('Chicago Headquarters', 'Office', 108),
('Atlanta Regional Office', 'Office', 109),
('Boston Corporate Center', 'Office', 110),

-- Dealerships & Service Centers
('LA Premium Auto Mall', 'Dealership', 111),
('Miami Motors Dealership', 'Dealership', 112),
('Phoenix Auto Gallery', 'Dealership', 113),

-- Service Centers
('Seattle Service Hub', 'Service Center', 141),
('Denver Maintenance Center', 'Service Center', 142),
('Houston Service Complex', 'Service Center', 143),

-- Warehouses
('Memphis Central Warehouse', 'Warehouse', 147),
('Louisville Distribution Center', 'Warehouse', 148),
('Jacksonville Storage Facility', 'Warehouse', 149),

-- Additional Dealerships
('San Francisco Bay Dealership', 'Dealership', 128),
('Dallas Premium Center', 'Dealership', 137),
('Austin Luxury Cars', 'Dealership', 117),
('Portland Motors', 'Dealership', 115),
('San Diego Auto Gallery', 'Dealership', 118),

-- Additional Service Centers
('Cincinnati Service Excellence', 'Service Center', 141),
('Milwaukee Maintenance Hub', 'Service Center', 142),
('Oklahoma City Service Center', 'Service Center', 143),

-- Additional Offices
('Hartford Business Center', 'Office', 144),
('Richmond Corporate Hub', 'Office', 145),
('Providence Office Complex', 'Office', 146),

-- Regional Warehouses
('Northeast Distribution Center', 'Warehouse', 124),
('Southeast Storage Hub', 'Warehouse', 125),
('Midwest Logistics Center', 'Warehouse', 126),

-- Additional Factories
('Nashville Production Plant', 'Factory', 119),
('Indianapolis Assembly Center', 'Factory', 132),
('Kansas City Manufacturing', 'Factory', 126),

-- Mixed-Use Facilities
('Las Vegas Auto Complex', 'Dealership', 121),
('Minneapolis Auto Center', 'Dealership', 123),
('Salt Lake City Motors', 'Dealership', 122),

-- Service and Sales Combined
('Philadelphia Auto Plaza', 'Service Center', 124),
('Cleveland Motor World', 'Dealership', 125),
('St. Louis Auto Complex', 'Service Center', 134),

-- Regional Offices
('New York Regional HQ', 'Office', 127),
('Washington DC Office', 'Office', 129),
('Sacramento Branch', 'Office', 130),

-- Additional Service Locations
('Raleigh Service Point', 'Service Center', 131),
('Charlotte Auto Care', 'Service Center', 133),
('Pittsburgh Service Hub', 'Service Center', 135),

-- Specialty Centers
('Orlando Performance Center', 'Service Center', 136),
('Tampa Custom Shop', 'Service Center', 150),
('Fort Lauderdale Luxury Service', 'Service Center', 152),

-- Distribution Centers
('Albuquerque Distribution', 'Warehouse', 150),
('Tucson Logistics Center', 'Warehouse', 151),
('Fresno Storage Facility', 'Warehouse', 152),

-- Additional Mixed Use
('Honolulu Auto Complex', 'Dealership', 153),
('Anchorage Motors', 'Dealership', 154),
('Baltimore Auto Center', 'Dealership', 155),
('Columbus Full Service', 'Service Center', 156),

-- International Locations
('Toronto Canada Branch', 'Office', 139),
('Mexico City Operations', 'Office', 140);

SELECT AddressID, StreetAddress, City, AddressType 
FROM Addresses 
ORDER BY AddressID;
-- supplers 


-- First delete existing data
DELETE FROM Suppliers;


-- Insert new suppliers with proper foreign key references
INSERT INTO Suppliers (SupplierID, SupplierName, ContactPerson, ContactEmail, PrimaryAddressID) VALUES
-- Tier 1 Major Component Suppliers
(1, 'AutoTech Solutions', 'James Wilson', 'jwilson@autotech.com', 105),
(2, 'Elite Electronics Systems', 'Sarah Chen', 'schen@eliteelec.com', 106),
(3, 'PowerTrain Dynamics', 'Michael Rodriguez', 'mrodriguez@ptdynamics.com', 107),
(4, 'Global Chassis Corp', 'David Kim', 'dkim@globalchassis.com', 132),
(5, 'Premier Parts Manufacturing', 'Lisa Thompson', 'lthompson@premierparts.com', 147),

-- Electronics and Technology Suppliers
(6, 'Smart Systems Inc', 'Robert Chang', 'rchang@smartsys.com', 111),
(7, 'Connected Car Technologies', 'Emma Davis', 'edavis@connectedcar.com', 113),
(8, 'Digital Dashboard Solutions', 'Alan Moore', 'amoore@digidash.com', 128),
(9, 'Sensor Tech Industries', 'Patricia Lee', 'plee@sensortech.com', 130),
(10, 'AutoSoft Innovations', 'George Martinez', 'gmartinez@autosoft.com', 131),

-- Interior Components Suppliers
(11, 'Comfort Seating Systems', 'Nancy White', 'nwhite@comfortseating.com', 141),
(12, 'Interior Dynamics LLC', 'Kevin Johnson', 'kjohnson@interiordyn.com', 142),
(13, 'Luxury Trim Specialists', 'Maria Garcia', 'mgarcia@luxtrim.com', 143),
(14, 'Climate Control Corp', 'Thomas Brown', 'tbrown@climatecorp.com', 144),
(15, 'Acoustic Solutions Ltd', 'Jennifer Wilson', 'jwilson@acousticsol.com', 145),

-- Exterior and Body Components
(16, 'MetalForm Industries', 'Richard Lee', 'rlee@metalform.com', 146),
(17, 'Advanced Composites Corp', 'Susan Miller', 'smiller@advcomp.com', 147),
(18, 'GlassTech Solutions', 'Paul Anderson', 'panderson@glasstech.com', 148),
(19, 'Lighting Systems International', 'Diana Taylor', 'dtaylor@lsi.com', 149),
(20, 'Paint & Finish Specialists', 'Carlos Ruiz', 'cruiz@paintfinish.com', 150),

-- Powertrain Components
(21, 'Engine Technologies Inc', 'Mark Williams', 'mwilliams@enginetech.com', 124),
(22, 'Transmission Dynamics', 'Laura Chen', 'lchen@transdyn.com', 125),
(23, 'Hybrid Systems Corp', 'Steven Jones', 'sjones@hybridsys.com', 126),
(24, 'Electric Drive Solutions', 'Rachel Kim', 'rkim@electricdrive.com', 127),
(25, 'Brake Systems Advanced', 'Brian Miller', 'bmiller@brakesys.com', 129),

-- Safety System Suppliers
(26, 'SafetyFirst Systems', 'Amanda Peters', 'apeters@safetyfirst.com', 151),
(27, 'Airbag Technologies', 'Eric Johnson', 'ejohnson@airbagtec.com', 152),
(28, 'Sensor Safety Corp', 'Michelle Lee', 'mlee@sensorsafety.com', 153),
(29, 'Guardian Systems Ltd', 'Chris Thompson', 'cthompson@guardian.com', 154),
(30, 'Protective Equipment Inc', 'Daniel Harris', 'dharris@protectequip.com', 155),

-- Raw Materials Suppliers
(31, 'Steel Dynamics Corp', 'Frank Anderson', 'fanderson@steeldyn.com', 112),
(32, 'Aluminum Solutions', 'Helen Martinez', 'hmartinez@alusol.com', 114),
(33, 'Polymer Technologies', 'Wayne Davis', 'wdavis@polytech.com', 115),
(34, 'Advanced Materials Inc', 'Gloria Rodriguez', 'grodriguez@advmat.com', 116),
(35, 'Composite Structures LLC', 'Peter Chang', 'pchang@composites.com', 117),

-- Specialized Component Suppliers
(36, 'Performance Parts Pro', 'Tracy Wilson', 'twilson@perfparts.com', 118),
(37, 'Custom Components Ltd', 'Isaac Brown', 'ibrown@customcomp.com', 119),
(38, 'Precision Engineering Corp', 'Olivia Martin', 'omartin@precision.com', 120),
(39, 'Innovation Systems', 'Kyle Thompson', 'kthompson@innovsys.com', 121),
(40, 'Quality Components Inc', 'Nina Patel', 'npatel@qualitycomp.com', 122),

-- International Suppliers
(41, 'Canadian Auto Parts', 'John MacDonald', 'jmacdonald@canparts.com', 139),
(42, 'Mexican Components SA', 'Luis Hernandez', 'lhernandez@mexcomp.com', 140),
(43, 'European Systems GmbH', 'Anna Schmidt', 'aschmidt@eurosys.com', 108),
(44, 'Asian Technologies Ltd', 'James Wong', 'jwong@asiantech.com', 109),
(45, 'Global Supply Co', 'Mary Johnson', 'mjohnson@globalsup.com', 110),

-- Specialized Technology Suppliers
(46, 'Battery Tech Solutions', 'William Chen', 'wchen@batterytech.com', 133),
(47, 'Autonomous Systems Inc', 'Rebecca Lewis', 'rlewis@autosys.com', 134),
(48, 'Connected Vehicle Corp', 'Howard Grant', 'hgrant@connectedveh.com', 135),
(49, 'Smart Sensor Solutions', 'Karen Wu', 'kwu@smartsensor.com', 136),
(50, 'AI Automotive Systems', 'Ted Richards', 'trichards@aiauto.com', 137);

-- First delete existing data and reset sequence
DELETE FROM Components;
ALTER SEQUENCE components_componentid_seq RESTART WITH 1;

INSERT INTO Components (ComponentID, ComponentName, Description, Category, UnitCost, Material, SupplierID) VALUES
-- Engine Components (from Power Train Dynamics - ID 3)
(1, 'V6 Engine Block', 'Standard 3.0L V6 engine block', 'Engine', 3200.00, 'Aluminum Alloy', 3),
(2, 'V8 Engine Block', 'Premium 4.0L V8 engine block', 'Engine', 4500.00, 'Aluminum Alloy', 3),
(3, 'Cylinder Head', 'Performance cylinder head assembly', 'Engine', 850.00, 'Aluminum', 21), -- Engine Technologies Inc
(4, 'Crankshaft', 'Forged steel crankshaft', 'Engine', 600.00, 'Steel', 21),
(5, 'Piston Set', 'High-performance piston set', 'Engine', 400.00, 'Aluminum Alloy', 21),

-- Transmission Components (Transmission Dynamics - ID 22)
(6, 'Automatic Transmission', '8-speed automatic transmission', 'Transmission', 2800.00, 'Various', 22),
(7, 'Manual Transmission', '6-speed manual transmission', 'Transmission', 2200.00, 'Various', 22),
(8, 'Transmission Control Module', 'Electronic control unit', 'Electronics', 450.00, 'Electronic', 22),
(9, 'Clutch Assembly', 'Heavy-duty clutch system', 'Transmission', 380.00, 'Various', 22),
(10, 'Gear Set', 'Precision-engineered gear set', 'Transmission', 750.00, 'Hardened Steel', 22),

-- Electronics (Smart Systems Inc - ID 6, Connected Car Technologies - ID 7, Digital Dashboard Solutions - ID 8)
(11, 'Engine Control Unit', 'Main engine management system', 'Electronics', 890.00, 'Electronic', 6),
(12, 'Infotainment System', 'Premium entertainment and navigation', 'Electronics', 1200.00, 'Electronic', 7),
(13, 'Digital Dashboard', '12.3" digital instrument cluster', 'Electronics', 980.00, 'Electronic', 8),
(14, 'Battery Management System', 'Advanced BMS for hybrids', 'Electronics', 650.00, 'Electronic', 46), -- Battery Tech Solutions
(15, 'LED Headlight Assembly', 'Adaptive LED lighting system', 'Lighting', 450.00, 'Various', 19), -- Lighting Systems International

-- Interior Components (Comfort Seating - ID 11, Interior Dynamics - ID 12, etc.)
(16, 'Leather Seat Set', 'Premium leather seat assembly', 'Interior', 2200.00, 'Leather', 11),
(17, 'Dashboard Assembly', 'Complete dashboard unit', 'Interior', 1500.00, 'Plastic/Various', 12),
(18, 'Climate Control Unit', 'Dual-zone climate system', 'Interior', 580.00, 'Various', 14), -- Climate Control Corp
(19, 'Door Panel Set', 'Premium door panels', 'Interior', 800.00, 'Various', 13), -- Luxury Trim Specialists
(20, 'Center Console', 'Storage and control console', 'Interior', 400.00, 'Plastic/Leather', 13),

-- Safety Components (Safety suppliers IDs 26-30)
(21, 'Airbag System', 'Complete airbag safety system', 'Safety', 600.00, 'Various', 27), -- Airbag Technologies
(22, 'ABS Module', 'Anti-lock braking system', 'Safety', 420.00, 'Electronic', 26), -- SafetyFirst Systems
(23, 'Radar Sensor', 'Forward collision detection', 'Safety', 380.00, 'Electronic', 28), -- Sensor Safety Corp
(24, 'Camera System', '360-degree camera system', 'Safety', 750.00, 'Electronic', 29), -- Guardian Systems Ltd
(25, 'Stability Control Module', 'Electronic stability control', 'Safety', 480.00, 'Electronic', 26),

-- Exterior Components (MetalForm - ID 16, Advanced Composites - ID 17, GlassTech - ID 18)
(26, 'Hood Assembly', 'Lightweight hood structure', 'Exterior', 580.00, 'Aluminum', 16),
(27, 'Door Shell Set', 'Complete door structures', 'Exterior', 1200.00, 'Steel', 16),
(28, 'Windshield', 'Acoustic laminated glass', 'Exterior', 450.00, 'Glass', 18),
(29, 'Bumper Assembly', 'Front bumper with sensors', 'Exterior', 380.00, 'Composite', 17),
(30, 'Side Mirror Set', 'Power-folding mirrors', 'Exterior', 290.00, 'Various', 19),

-- Chassis Components (Global Chassis Corp - ID 4)
(31, 'Chassis Frame', 'Main vehicle frame', 'Chassis', 2800.00, 'High-Strength Steel', 4),
(32, 'Suspension System', 'Adaptive suspension setup', 'Chassis', 1500.00, 'Various', 4),
(33, 'Brake System', 'Performance brake package', 'Chassis', 980.00, 'Various', 25), -- Brake Systems Advanced
(34, 'Wheel Hub Assembly', 'Precision wheel bearing hub', 'Chassis', 180.00, 'Steel', 4),
(35, 'Control Arms', 'Suspension control arms', 'Chassis', 250.00, 'Aluminum', 4),

-- Powertrain Components (PowerTrain Dynamics - ID 3)
(36, 'Drive Shaft', 'High-performance drive shaft', 'Powertrain', 420.00, 'Steel', 3),
(37, 'Differential', 'Limited-slip differential', 'Powertrain', 890.00, 'Steel', 3),
(38, 'Transfer Case', '4WD transfer case', 'Powertrain', 1200.00, 'Various', 3),
(39, 'CV Joint Set', 'Constant velocity joints', 'Powertrain', 180.00, 'Steel', 3),
(40, 'Axle Assembly', 'Complete axle system', 'Powertrain', 750.00, 'Steel', 3),

-- Specialized Technology (Battery Tech - ID 46, Autonomous Systems - ID 47, Connected Vehicle - ID 48)
(41, 'Battery Pack', 'Hybrid battery system', 'Electric', 3800.00, 'Various', 46),
(42, 'Electric Motor', 'Hybrid drive motor', 'Electric', 2200.00, 'Various', 47),
(43, 'Autonomous Driving Unit', 'Self-driving computer', 'Electronics', 4500.00, 'Electronic', 47),
(44, 'LiDAR Sensor', 'Advanced distance sensing', 'Electronics', 1800.00, 'Electronic', 48),
(45, 'Vehicle Control Module', 'Central control unit', 'Electronics', 1200.00, 'Electronic', 48),

-- Raw Material Components (IDs 31-35)
(46, 'Steel Frame Rails', 'Structural frame components', 'Structure', 380.00, 'Steel', 31), -- Steel Dynamics Corp
(47, 'Aluminum Panels', 'Body panels', 'Structure', 290.00, 'Aluminum', 32), -- Aluminum Solutions
(48, 'Carbon Fiber Roof', 'Lightweight roof panel', 'Structure', 1500.00, 'Carbon Fiber', 34), -- Advanced Materials Inc
(49, 'Polymer Dashboard Base', 'Dashboard substrate', 'Interior', 180.00, 'Polymer', 33), -- Polymer Technologies
(50, 'Composite Floor Pan', 'Structural floor component', 'Structure', 450.00, 'Composite', 35); -- Composite Structures LLC

--departments 

INSERT INTO Departments (DepartmentName, ManagerID) VALUES
-- Executive and Administrative
('Executive Office', NULL),
('Corporate Administration', NULL),
('Legal Affairs', NULL),
('Corporate Communications', NULL),
('Internal Audit', NULL),

-- Manufacturing Operations
('Vehicle Assembly', NULL),
('Quality Control', NULL),
('Production Planning', NULL),
('Manufacturing Engineering', NULL),
('Plant Maintenance', NULL),

-- Engineering
('Product Engineering', NULL),
('Powertrain Engineering', NULL),
('Electrical Systems Engineering', NULL),
('Chassis Engineering', NULL),
('Safety Engineering', NULL),

-- Research and Development
('Research & Development', NULL),
('Innovation Lab', NULL),
('Advanced Technologies', NULL),
('Electric Vehicle Development', NULL),
('Autonomous Systems', NULL),

-- Supply Chain
('Supply Chain Management', NULL),
('Procurement', NULL),
('Inventory Management', NULL),
('Logistics', NULL),
('Supplier Relations', NULL),

-- Sales and Marketing
('Sales Operations', NULL),
('Marketing', NULL),
('Brand Management', NULL),
('Market Research', NULL),
('Dealer Relations', NULL),

-- Customer Service
('Customer Experience', NULL),
('After Sales Service', NULL),
('Warranty Claims', NULL),
('Customer Support', NULL),
('Service Training', NULL),

-- Finance and Accounting
('Finance', NULL),
('Accounting', NULL),
('Financial Planning', NULL),
('Cost Management', NULL),
('Treasury', NULL),

-- Human Resources
('Human Resources', NULL),
('Talent Acquisition', NULL),
('Employee Relations', NULL),
('Training & Development', NULL),
('Compensation & Benefits', NULL),

-- Information Technology
('IT Operations', NULL),
('Software Development', NULL),
('Network Infrastructure', NULL),
('Cybersecurity', NULL),
('Digital Transformation', NULL),

-- Additional Operating Departments
('Quality Assurance', NULL),
('Environmental Health & Safety', NULL),
('Facilities Management', NULL),
('Project Management Office', NULL),
('Business Intelligence', NULL),
('Compliance', NULL),
('Risk Management', NULL),
('Strategic Planning', NULL),
('Global Operations', NULL),
('Innovation Management', NULL);

-- employee 

-- 1. CEO (Top of hierarchy)
INSERT INTO Employees (
    FirstName, LastName, JobTitle, DepartmentID, HireDate, TerminationDate, 
    Status, SalaryOrRate, PayType, Email, WorkPhone, LocationID, HomeAddressID, SupervisorID
) VALUES
('John', 'Mitchell', 'Chief Executive Officer', 1, '2020-01-15', NULL, 'Active', 350000.00, 'Salary', 
 'john.mitchell@autocompany.com', '555-0001', 172, 105, NULL);

-- 2. C-Level Executives (Report to CEO)

INSERT INTO Employees (
    FirstName, LastName, JobTitle, DepartmentID, HireDate, TerminationDate, 
    Status, SalaryOrRate, PayType, Email, WorkPhone, LocationID, HomeAddressID, SupervisorID
) VALUES
('Sarah', 'Chen', 'Chief Operating Officer', 1, '2020-03-20', NULL, 'Active', 280000.00, 'Salary',
 'sarah.chen@autocompany.com', '555-0002', 172, 106, 1),
('Michael', 'Rodriguez', 'Chief Financial Officer', 1, '2020-02-10', NULL, 'Active', 275000.00, 'Salary',
 'michael.rodriguez@autocompany.com', '555-0003', 172, 107, 94);

SELECT EmployeeID, FirstName, LastName, JobTitle 
FROM Employees 
ORDER BY EmployeeID;

-- 3. Directors (Report to COO/CFO)
INSERT INTO Employees (
    FirstName, LastName, JobTitle, DepartmentID, HireDate, TerminationDate, 
    Status, SalaryOrRate, PayType, Email, WorkPhone, LocationID, HomeAddressID, SupervisorID
) VALUES
-- Reports to COO (ID 99)
('David', 'Kim', 'Manufacturing Director', 6, '2020-04-15', NULL, 'Active', 180000.00, 'Salary',
 'david.kim@autocompany.com', '555-0004', 169, 108, 99),
('Robert', 'Chang', 'Chief Engineer', 11, '2020-05-12', NULL, 'Active', 190000.00, 'Salary',
 'robert.chang@autocompany.com', '555-0006', 170, 110, 99),
('Alan', 'Moore', 'R&D Director', 16, '2020-08-20', NULL, 'Active', 175000.00, 'Salary',
 'alan.moore@autocompany.com', '555-0008', 171, 112, 99),
('George', 'Martinez', 'Supply Chain Director', 21, '2020-10-01', NULL, 'Active', 165000.00, 'Salary',
 'george.martinez@autocompany.com', '555-0010', 173, 114, 99),
('Kevin', 'Johnson', 'Sales Director', 26, '2021-01-10', NULL, 'Active', 170000.00, 'Salary',
 'kevin.johnson@autocompany.com', '555-0012', 174, 116, 99),
('Charles', 'Evans', 'Customer Service Director', 31, '2021-09-01', NULL, 'Active', 150000.00, 'Salary',
 'charles.evans@autocompany.com', '555-0020', 175, 124, 99),

-- Reports to CFO (ID 100)
('Brian', 'Walker', 'Finance Controller', 36, '2021-11-05', NULL, 'Active', 155000.00, 'Salary',
 'brian.walker@autocompany.com', '555-0022', 172, 126, 100),
('Steven', 'Young', 'HR Manager', 41, '2022-01-15', NULL, 'Active', 130000.00, 'Salary',
 'steven.young@autocompany.com', '555-0024', 173, 128, 100),
('Edward', 'Hernandez', 'IT Director', 46, '2022-03-01', NULL, 'Active', 145000.00, 'Salary',
 'edward.hernandez@autocompany.com', '555-0026', 174, 130, 100);

INSERT INTO Employees (
    FirstName, LastName, JobTitle, DepartmentID, HireDate, TerminationDate,
    Status, SalaryOrRate, PayType, Email, WorkPhone, LocationID, HomeAddressID, SupervisorID
) VALUES
-- Reports to Manufacturing Director (101)
('Lisa', 'Thompson', 'Quality Control Manager', 7, '2020-06-01', NULL, 'Active', 150000.00, 'Salary',
'lisa.thompson@autocompany.com', '555-0005', 169, 109, 101),

-- Reports to Chief Engineer (102)
('Emma', 'Davis', 'Electrical Systems Lead', 13, '2020-07-15', NULL, 'Active', 160000.00, 'Salary',
'emma.davis@autocompany.com', '555-0007', 170, 111, 102),

-- Reports to R&D Director (103)
('Patricia', 'Lee', 'Innovation Lab Manager', 17, '2020-09-10', NULL, 'Active', 145000.00, 'Salary',
'patricia.lee@autocompany.com', '555-0009', 171, 113, 103),

-- Reports to Supply Chain Director (104)
('Nancy', 'White', 'Procurement Manager', 22, '2020-11-15', NULL, 'Active', 135000.00, 'Salary',
'nancy.white@autocompany.com', '555-0011', 173, 115, 104),

-- Reports to Sales Director (105)
('Maria', 'Garcia', 'Marketing Manager', 27, '2021-02-15', NULL, 'Active', 140000.00, 'Salary',
'maria.garcia@autocompany.com', '555-0013', 174, 117, 105),

-- Reports to Customer Service Director (106)
('Laura', 'Scott', 'Support Manager', 32, '2021-10-12', NULL, 'Active', 110000.00, 'Salary',
'laura.scott@autocompany.com', '555-0021', 175, 125, 106),

-- Reports to Finance Controller (107)
('Angela', 'Hall', 'Accountant', 37, '2021-12-10', NULL, 'Active', 90000.00, 'Salary',
'angela.hall@autocompany.com', '555-0023', 172, 127, 107),

-- Reports to HR Manager (108)
('Karen', 'Baker', 'Recruiter', 42, '2022-02-20', NULL, 'Active', 85000.00, 'Salary',
'karen.baker@autocompany.com', '555-0025', 173, 129, 108),

-- Reports to IT Director (109)
('Betty', 'Lopez', 'Software Developer', 47, '2022-04-15', NULL, 'Active', 95000.00, 'Salary',
'betty.lopez@autocompany.com', '555-0027', 174, 131, 109),

-- Reports to Manufacturing Director (101)
('Frank', 'Gonzalez', 'EH&S Specialist', 48, '2022-05-10', NULL, 'Active', 87000.00, 'Salary',
'frank.gonzalez@autocompany.com', '555-0028', 176, 132, 101),

-- Reports to CFO (100)
('Deborah', 'Perez', 'Compliance Officer', 49, '2022-06-20', NULL, 'Active', 98000.00, 'Salary',
'deborah.perez@autocompany.com', '555-0029', 176, 133, 100);

-- 5. Staff Level with corrected supervisor IDs
INSERT INTO Employees (
   FirstName, LastName, JobTitle, DepartmentID, HireDate, TerminationDate,
   Status, SalaryOrRate, PayType, Email, WorkPhone, LocationID, HomeAddressID, SupervisorID
) VALUES
-- Reports to Quality Control Manager (121)
('Thomas', 'Brown', 'Assembly Line Worker', 6, '2021-03-01', NULL, 'Active', 25.00, 'Hourly',
'thomas.brown@autocompany.com', '555-0014', 169, 118, 121),
('Jennifer', 'Wilson', 'Quality Inspector', 7, '2021-04-15', NULL, 'Active', 28.00, 'Hourly',
'jennifer.wilson@autocompany.com', '555-0015', 169, 119, 121),

-- Reports to Electrical Systems Lead (122)
('Richard', 'Lee', 'Mechanical Engineer', 11, '2021-05-20', NULL, 'Active', 95000.00, 'Salary',
'richard.lee@autocompany.com', '555-0016', 170, 120, 122),
('Susan', 'Miller', 'Electrical Engineer', 13, '2021-06-10', NULL, 'Active', 92000.00, 'Salary',
'susan.miller@autocompany.com', '555-0017', 170, 121, 122),

-- Reports to Innovation Lab Manager (123)
('Paul', 'Anderson', 'Research Scientist', 16, '2021-07-01', NULL, 'Active', 98000.00, 'Salary',
'paul.anderson@autocompany.com', '555-0018', 171, 122, 123),
('Diana', 'Taylor', 'Innovation Specialist', 17, '2021-08-15', NULL, 'Active', 88000.00, 'Salary',
'diana.taylor@autocompany.com', '555-0019', 171, 123, 123),

-- Reports to Quality Control Manager (121)
('Ethan', 'King', 'Technician', 10, '2022-07-10', NULL, 'Active', 30.00, 'Hourly',
'ethan.king@autocompany.com', '555-0030', 169, 134, 121),

-- Reports to Angela Hall in Finance (127)
('Natalie', 'Price', 'Data Entry Clerk', 37, '2022-08-15', NULL, 'Active', 24.00, 'Hourly',
'natalie.price@autocompany.com', '555-0031', 172, 135, 127);



-- workorders 

INSERT INTO WorkOrders (ProductID, Quantity, DateCreated, DueDate, Status) VALUES
-- Velocity Series Work Orders (Sedans)
(1, 150, '2024-01-15', '2024-03-15', 'Completed'),
(2, 200, '2024-01-20', '2024-03-20', 'Completed'),
(3, 100, '2024-02-01', '2024-04-01', 'In Progress'),
(4, 75, '2024-02-15', '2024-04-15', 'In Progress'),
(1, 125, '2024-03-01', '2024-05-01', 'Pending'),
(2, 175, '2024-03-15', '2024-05-15', 'Pending'),
(3, 80, '2024-02-10', '2024-04-10', 'In Progress'),
(4, 90, '2024-02-20', '2024-04-20', 'In Progress'),
(6, 60, '2024-01-05', '2024-03-05', 'Cancelled'),     -- Changed from 5 to 6 (Active model)
(6, 100, '2024-03-10', '2024-05-10', 'Pending'),

-- Atlas Series Work Orders (SUVs)
(11, 200, '2024-01-10', '2024-03-10', 'Completed'),
(12, 250, '2024-01-25', '2024-03-25', 'Completed'),
(13, 150, '2024-02-05', '2024-04-05', 'In Progress'),
(14, 100, '2024-02-25', '2024-04-25', 'In Progress'),
(11, 175, '2024-03-05', '2024-05-05', 'Pending'),
(12, 225, '2024-03-20', '2024-05-20', 'Pending'),
(13, 120, '2024-02-15', '2024-04-15', 'In Progress'),
(14, 80, '2024-01-30', '2024-03-30', 'Completed'),
(16, 50, '2024-01-08', '2024-03-08', 'Cancelled'),    -- Changed from 15 to 16 (Active model)
(16, 150, '2024-03-12', '2024-05-12', 'Pending'),

-- Horizon Series Work Orders (Crossovers)
(21, 175, '2024-01-12', '2024-03-12', 'Completed'),
(22, 200, '2024-01-28', '2024-03-28', 'Completed'),
(23, 125, '2024-02-08', '2024-04-08', 'In Progress'),
(24, 150, '2024-02-28', '2024-04-28', 'In Progress'),
(21, 160, '2024-03-08', '2024-05-08', 'Pending'),
(22, 180, '2024-03-22', '2024-05-22', 'Pending'),
(23, 140, '2024-02-18', '2024-04-18', 'In Progress'),
(24, 120, '2024-02-22', '2024-04-22', 'In Progress'),
(26, 40, '2024-01-15', '2024-03-15', 'Cancelled'),    -- Changed from 25 to 26 (Active model)
(26, 130, '2024-03-15', '2024-05-15', 'Pending'),

-- Titan Series Work Orders (Trucks)
(31, 100, '2024-01-18', '2024-03-18', 'Completed'),
(32, 150, '2024-01-30', '2024-03-30', 'Completed'),
(33, 80, '2024-02-12', '2024-04-12', 'In Progress'),
(34, 120, '2024-03-01', '2024-05-01', 'Pending'),
(31, 90, '2024-03-10', '2024-05-10', 'Pending'),
(32, 130, '2024-03-25', '2024-05-25', 'Pending'),
(33, 75, '2024-02-20', '2024-04-20', 'In Progress'),
(34, 100, '2024-02-25', '2024-04-25', 'In Progress'),
(36, 30, '2024-01-20', '2024-03-20', 'Cancelled'),    -- Changed from 35 to 36 (Active model)
(36, 110, '2024-03-18', '2024-05-18', 'Pending'),

-- Spark Series Work Orders (Electric Vehicles)
(41, 125, '2024-01-22', '2024-03-22', 'Completed'),
(42, 175, '2024-02-02', '2024-04-02', 'In Progress'),
(43, 100, '2024-02-15', '2024-04-15', 'In Progress'),
(44, 150, '2024-03-05', '2024-05-05', 'Pending'),
(41, 115, '2024-03-12', '2024-05-12', 'Pending'),
(42, 160, '2024-03-28', '2024-05-28', 'Pending'),
(43, 90, '2024-02-22', '2024-04-22', 'In Progress'),
(44, 135, '2024-02-28', '2024-04-28', 'In Progress'),
(46, 25, '2024-01-25', '2024-03-25', 'Cancelled'),    -- Changed from 45 to 46 (Active model)
(46, 140, '2024-03-20', '2024-05-20', 'Pending');


-- Update Departments with ManagerIDs based on our employee records
UPDATE Departments 
SET ManagerID = CASE DepartmentName
    -- Executive Office (CEO - John Mitchell)
    WHEN 'Executive Office' THEN 94
    
    -- Main departments under COO (Sarah Chen - 99)
    WHEN 'Vehicle Assembly' THEN 101    -- David Kim (Manufacturing Director)
    WHEN 'Product Engineering' THEN 102 -- Robert Chang (Chief Engineer)
    WHEN 'Research & Development' THEN 103 -- Alan Moore (R&D Director)
    WHEN 'Supply Chain Management' THEN 104 -- George Martinez (Supply Chain Director)
    WHEN 'Sales Operations' THEN 105    -- Kevin Johnson (Sales Director)
    WHEN 'Customer Experience' THEN 106 -- Charles Evans (Customer Service Director)
    
    -- Departments under CFO (Michael Rodriguez - 100)
    WHEN 'Finance' THEN 107    -- Brian Walker (Finance Controller)
    WHEN 'Human Resources' THEN 108  -- Steven Young (HR Manager)
    WHEN 'IT Operations' THEN 109    -- Edward Hernandez (IT Director)
    
    -- Other key managers
    WHEN 'Quality Control' THEN 121     -- Lisa Thompson (Quality Control Manager)
    WHEN 'Electrical Systems Engineering' THEN 122 -- Emma Davis (Electrical Systems Lead)
    WHEN 'Innovation Lab' THEN 123      -- Patricia Lee (Innovation Lab Manager)
    WHEN 'Procurement' THEN 124         -- Nancy White (Procurement Manager)
    WHEN 'Marketing' THEN 125           -- Maria Garcia (Marketing Manager)
    WHEN 'Customer Support' THEN 126    -- Laura Scott (Support Manager)
    WHEN 'Accounting' THEN 127          -- Angela Hall (Accountant)
    WHEN 'Talent Acquisition' THEN 128  -- Karen Baker (Recruiter)
    WHEN 'Software Development' THEN 129 -- Betty Lopez (Software Developer)
    WHEN 'Environmental Health & Safety' THEN 130 -- Frank Gonzalez (EH&S Specialist)
    WHEN 'Compliance' THEN 131          -- Deborah Perez (Compliance Officer)
    
    ELSE NULL -- Keep other departments' ManagerID as NULL for now
END;

SELECT AddressID, StreetAddress, City, State, Country, AddressType 
FROM Addresses 
WHERE AddressType IN ('Primary', 'Work', 'Site')
ORDER BY AddressID;

-- customers 

INSERT INTO Customers (
    FirstName, LastName, CompanyName, Email, Phone, 
    PrimaryAddressID, RegistrationDate, LoyaltyPointsBalance
) VALUES
-- Corporate Customers (using Work/Site addresses)
(NULL, NULL, 'Fleet Motors Inc', 'fleet@fleetmotors.com', '555-0100', 108, '2023-01-15', 5000),
(NULL, NULL, 'Luxury Car Rentals', 'info@luxuryrentals.com', '555-0101', 109, '2023-02-20', 7500),
(NULL, NULL, 'City Taxi Corporation', 'fleet@citytaxi.com', '555-0102', 110, '2023-03-10', 10000),
(NULL, NULL, 'Express Delivery Services', 'fleet@expressdelivery.com', '555-0103', 131, '2023-04-05', 8000),
(NULL, NULL, 'Corporate Fleet Solutions', 'info@corpfleet.com', '555-0104', 144, '2023-05-15', 15000),

-- Individual Customers - High Value (using Primary addresses)
('Robert', 'Anderson', NULL, 'r.anderson@email.com', '555-0105', 119, '2023-06-01', 3000),
('Maria', 'Garcia', NULL, 'm.garcia@email.com', '555-0106', 120, '2023-06-15', 2800),
('James', 'Wilson', NULL, 'j.wilson@email.com', '555-0107', 121, '2023-07-01', 4200),
('Emily', 'Brown', NULL, 'e.brown@email.com', '555-0108', 122, '2023-07-15', 3500),
('Michael', 'Taylor', NULL, 'm.taylor@email.com', '555-0109', 123, '2023-08-01', 5000),

-- Individual Customers - Regular (using Primary addresses)
('David', 'Martinez', NULL, 'd.martinez@email.com', '555-0110', 130, '2023-08-15', 1500),
('Sarah', 'Johnson', NULL, 's.johnson@email.com', '555-0111', 136, '2023-09-01', 1200),
('Thomas', 'Lee', NULL, 't.lee@email.com', '555-0112', 137, '2023-09-15', 800),
('Jennifer', 'White', NULL, 'j.white@email.com', '555-0113', 138, '2023-10-01', 1000),
('Christopher', 'Harris', NULL, 'c.harris@email.com', '555-0114', 153, '2023-10-15', 500),

-- Corporate Customers - Medium Size (using Work/Site addresses)
(NULL, NULL, 'Tech Transport Solutions', 'fleet@techts.com', '555-0115', 145, '2023-11-01', 6000),
(NULL, NULL, 'Green Fleet Services', 'info@greenfleet.com', '555-0116', 146, '2023-11-15', 4500),
(NULL, NULL, 'Regional Delivery Co', 'fleet@regdelivery.com', '555-0117', 154, '2023-12-01', 5500),
(NULL, NULL, 'Urban Mobility Group', 'info@urbanmobility.com', '555-0118', 155, '2023-12-15', 7000),
(NULL, NULL, 'Executive Car Services', 'fleet@execcar.com', '555-0119', 132, '2024-01-01', 8500),

-- International Customers (using international addresses)
('Jean', 'Dubois', NULL, 'j.dubois@email.com', '555-0120', 139, '2024-01-15', 2000),
('Hans', 'Schmidt', NULL, 'h.schmidt@email.com', '555-0121', 139, '2024-02-01', 1800),
(NULL, NULL, 'Canadian Fleet Management', 'info@canfleet.com', '555-0122', 139, '2024-02-15', 9000),
(NULL, NULL, 'Mexico Transport Solutions', 'info@mextransport.com', '555-0123', 140, '2024-03-01', 7500),

-- Recent Customers (using Primary addresses)
('William', 'Davis', NULL, 'w.davis@email.com', '555-0124', 156, '2024-03-15', 200),
('Emma', 'Wilson', NULL, 'e.wilson@email.com', '555-0125', 119, '2024-04-01', 300),
('Oliver', 'Thompson', NULL, 'o.thompson@email.com', '555-0126', 120, '2024-04-15', 150),
('Sophia', 'Rodriguez', NULL, 's.rodriguez@email.com', '555-0127', 121, '2024-05-01', 250),
('Lucas', 'Martinez', NULL, 'l.martinez@email.com', '555-0128', 122, '2024-05-15', 100),
('Isabella', 'Clark', NULL, 'i.clark@email.com', '555-0129', 123, '2024-06-01', 50);

-- product feature 

INSERT INTO ProductFeatures (ProductID, FeatureID) VALUES
-- Velocity Series (Sedans)
-- Base Model S1 (ID 1) - Essential Features
(1, 3),  -- Lane Departure Warning
(1, 4),  -- Blind Spot Detection
(1, 8),  -- Parking Sensors
(1, 12), -- Heated Front Seats
(1, 19), -- Wireless Phone Charging

-- Sport Model S2 (ID 2) - Performance Features
(2, 1),  -- Advanced Driver Assistance
(2, 2),  -- 360-Degree Camera
(2, 31), -- Sport Suspension
(2, 32), -- Performance Brakes
(2, 33), -- Sport Exhaust
(2, 37), -- Performance Tires
(2, 38), -- Engine Power Upgrade

-- Luxury Model S3 (ID 3) - Premium Features
(3, 11), -- Premium Leather Seats
(3, 13), -- Ventilated Seats
(3, 14), -- Massage Seats
(3, 15), -- Panoramic Sunroof
(3, 16), -- Ambient Lighting
(3, 17), -- Four-Zone Climate Control
(3, 18), -- Premium Sound System

-- Executive Model S4 (ID 4) - All Features
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5),  -- All Safety Features
(4, 11), (4, 12), (4, 13), (4, 14),      -- All Interior Features
(4, 41), (4, 42), (4, 43), (4, 44),      -- All Tech Features

-- Atlas Series (SUVs)
-- Base X1 (ID 11) - Essential SUV Features
(11, 1), -- Advanced Driver Assistance
(11, 4), -- Blind Spot Detection
(11, 8), -- Parking Sensors
(11, 24), -- Roof Rails
(11, 34), -- All-Wheel Drive

-- Premium X2 (ID 12) - Enhanced Features
(12, 1), (12, 2), (12, 3),               -- Safety Suite
(12, 11), (12, 12), (12, 15),            -- Comfort Features
(12, 21), (12, 22), (12, 23),            -- Exterior Enhancements
(12, 34), -- All-Wheel Drive

-- Luxury X3 (ID 13) - Premium SUV Features
(13, 1), (13, 2), (13, 3), (13, 4), (13, 5),  -- Full Safety Suite
(13, 11), (13, 12), (13, 13), (13, 14),       -- Full Interior Package
(13, 35), -- Adaptive Air Suspension
(13, 41), (13, 42), -- Tech Package

-- Horizon Series (Crossovers)
-- Base C1 (ID 21) - Essential Crossover Features
(21, 3), -- Lane Departure Warning
(21, 4), -- Blind Spot Detection
(21, 8), -- Parking Sensors
(21, 34), -- All-Wheel Drive

-- Plus C2 (ID 22) - Enhanced Features
(22, 1), (22, 2), (22, 3), (22, 4),      -- Safety Package
(22, 11), (22, 12), (22, 15),            -- Comfort Package
(22, 34), (22, 35),                      -- Advanced Drivetrain

-- Premium C3 (ID 23) - Premium Features
(23, 1), (23, 2), (23, 3), (23, 4), (23, 5),  -- Complete Safety
(23, 11), (23, 12), (23, 13), (23, 14),       -- Premium Interior
(23, 41), (23, 42), (23, 43),                 -- Tech Package

-- Titan Series (Trucks)
-- Base T1 (ID 31) - Essential Truck Features
(31, 4), -- Blind Spot Detection
(31, 8), -- Parking Sensors
(31, 24), -- Roof Rails
(31, 34), -- All-Wheel Drive

-- Pro T2 (ID 32) - Professional Features
(32, 1), (32, 2), (32, 3), (32, 4),      -- Safety Suite
(32, 31), (32, 32),                      -- Performance Package
(32, 34), (32, 35),                      -- Advanced Drivetrain

-- Heavy T3 (ID 33) - Premium Truck Features
(33, 1), (33, 2), (33, 3), (33, 4), (33, 5),  -- Full Safety
(33, 31), (33, 32), (33, 33), (33, 34),       -- Full Performance
(33, 41), (33, 42),                           -- Tech Package

-- Spark Series (Electric Vehicles)
-- Base E1 (ID 41) - Essential EV Features
(41, 3), -- Lane Departure Warning
(41, 4), -- Blind Spot Detection
(41, 8), -- Parking Sensors
(41, 41), -- Battery Management System

-- Plus E2 (ID 42) - Enhanced EV Features
(42, 1), (42, 2), (42, 3), (42, 4),      -- Safety Package
(42, 11), (42, 12), (42, 15),            -- Comfort Package
(42, 41), (42, 42), (42, 43),            -- Advanced EV Systems

-- Premium E3 (ID 43) - Premium EV Features
(43, 1), (43, 2), (43, 3), (43, 4), (43, 5),  -- Complete Safety
(43, 11), (43, 12), (43, 13), (43, 14),       -- Premium Interior
(43, 41), (43, 42), (43, 43), (43, 44),       -- Full Tech Suite
(43, 45)                                      -- Vehicle Control module

-- product components 

INSERT INTO ProductComponents (ProductID, ComponentID, QuantityRequired) VALUES
-- Velocity S1 (Base Sedan - ID 1)
(1, 1, 1),   -- V6 Engine Block
(1, 3, 1),   -- Cylinder Head
(1, 4, 1),   -- Crankshaft
(1, 5, 6),   -- Piston Set (6 for V6)
(1, 7, 1),   -- Manual Transmission
(1, 11, 1),  -- Engine Control Unit
(1, 16, 1),  -- Leather Seat Set
(1, 17, 1),  -- Dashboard Assembly
(1, 26, 1),  -- Hood Assembly
(1, 27, 4),  -- Door Shell Set
(1, 28, 1),  -- Windshield
(1, 31, 1),  -- Chassis Frame
(1, 32, 1),  -- Suspension System
(1, 33, 1),  -- Brake System
(1, 34, 4),  -- Wheel Hub Assembly (4 wheels)
(1, 36, 1),  -- Drive Shaft

-- Velocity S2 Sport (Sport Sedan - ID 2)
(2, 2, 1),   -- V8 Engine Block (upgrade from V6)
(2, 3, 1),   -- Cylinder Head
(2, 4, 1),   -- Crankshaft
(2, 5, 8),   -- Piston Set (8 for V8)
(2, 6, 1),   -- Automatic Transmission
(2, 11, 1),  -- Engine Control Unit
(2, 16, 1),  -- Leather Seat Set (Sport)
(2, 17, 1),  -- Dashboard Assembly
(2, 26, 1),  -- Hood Assembly
(2, 27, 4),  -- Door Shell Set
(2, 28, 1),  -- Windshield
(2, 31, 1),  -- Chassis Frame
(2, 32, 1),  -- Sport Suspension System
(2, 33, 1),  -- Performance Brake System
(2, 34, 4),  -- Wheel Hub Assembly
(2, 36, 1),  -- High-Performance Drive Shaft

-- Atlas X1 (Base SUV - ID 11)
(11, 2, 1),  -- V8 Engine Block
(11, 3, 1),  -- Cylinder Head
(11, 4, 1),  -- Crankshaft
(11, 5, 8),  -- Piston Set
(11, 6, 1),  -- Automatic Transmission
(11, 11, 1), -- Engine Control Unit
(11, 16, 2), -- Leather Seat Set (Two Rows)
(11, 17, 1), -- Dashboard Assembly
(11, 26, 1), -- Hood Assembly (Larger)
(11, 27, 4), -- Door Shell Set
(11, 28, 1), -- Windshield
(11, 31, 1), -- Reinforced Chassis Frame
(11, 32, 1), -- Heavy-Duty Suspension
(11, 33, 1), -- Brake System
(11, 34, 4), -- Wheel Hub Assembly
(11, 38, 1), -- Transfer Case (4WD)

-- Horizon C1 (Base Crossover - ID 21)
(21, 1, 1),  -- V6 Engine Block
(21, 3, 1),  -- Cylinder Head
(21, 4, 1),  -- Crankshaft
(21, 5, 6),  -- Piston Set
(21, 6, 1),  -- Automatic Transmission
(21, 11, 1), -- Engine Control Unit
(21, 16, 2), -- Leather Seat Set
(21, 17, 1), -- Dashboard Assembly
(21, 26, 1), -- Hood Assembly
(21, 27, 4), -- Door Shell Set
(21, 28, 1), -- Windshield
(21, 31, 1), -- Chassis Frame
(21, 32, 1), -- Suspension System
(21, 33, 1), -- Brake System
(21, 34, 4), -- Wheel Hub Assembly
(21, 38, 1), -- Transfer Case

-- Titan T1 (Base Truck - ID 31)
(31, 2, 1),  -- V8 Engine Block
(31, 3, 1),  -- Cylinder Head
(31, 4, 1),  -- Heavy-Duty Crankshaft
(31, 5, 8),  -- Piston Set
(31, 6, 1),  -- Heavy-Duty Automatic Transmission
(31, 11, 1), -- Engine Control Unit
(31, 16, 1), -- Leather Seat Set
(31, 17, 1), -- Dashboard Assembly
(31, 26, 1), -- Hood Assembly
(31, 27, 2), -- Door Shell Set (Regular Cab)
(31, 28, 1), -- Windshield
(31, 31, 1), -- Heavy-Duty Chassis Frame
(31, 32, 1), -- Heavy-Duty Suspension
(31, 33, 1), -- Heavy-Duty Brake System
(31, 34, 4), -- Heavy-Duty Wheel Hub Assembly
(31, 38, 1), -- Transfer Case

-- Spark E1 (Base Electric - ID 41)
(41, 41, 1), -- Battery Pack
(41, 42, 1), -- Electric Motor
(41, 14, 1), -- Battery Management System
(41, 11, 1), -- Vehicle Control Unit
(41, 16, 1), -- Leather Seat Set
(41, 17, 1), -- Dashboard Assembly
(41, 26, 1), -- Hood Assembly
(41, 27, 4), -- Door Shell Set
(41, 28, 1), -- Windshield
(41, 31, 1), -- Lightweight Chassis Frame
(41, 32, 1), -- EV-Specific Suspension
(41, 33, 1), -- Regenerative Brake System
(41, 34, 4), -- Wheel Hub Assembly
(41, 45, 1), -- Vehicle Control Module

-- Spark E3 Premium (Luxury Electric - ID 43)
(43, 41, 1), -- Enhanced Battery Pack
(43, 42, 2), -- Dual Electric Motors
(43, 14, 1), -- Advanced Battery Management System
(43, 11, 1), -- Enhanced Vehicle Control Unit
(43, 16, 1), -- Premium Leather Seat Set
(43, 17, 1), -- Premium Dashboard Assembly
(43, 26, 1), -- Hood Assembly
(43, 27, 4), -- Door Shell Set
(43, 28, 1), -- Premium Windshield
(43, 31, 1), -- Premium Chassis Frame
(43, 32, 1), -- Adaptive Suspension
(43, 33, 1), -- Performance Brake System
(43, 34, 4), -- Performance Wheel Hub Assembly
(43, 45, 1)  -- Advanced Vehicle Control module

--
--vehicle

INSERT INTO Vehicles (
   VIN, 
   ProductID, 
   ManufactureDate, 
   Color, 
   WorkOrderID, 
   CurrentMileage, 
   LastServiceDate, 
   CurrentStatus, 
   CurrentHolderCustomerID
) VALUES
-- Completed Work Orders - Velocity Series (WorkOrder 1-2)
('VEL1S12401', 1, '2024-02-01', 'Midnight Black', 1, 1000, '2024-03-15', 'Sold', 6),
('VEL1S12402', 1, '2024-02-01', 'Pearl White', 1, 500, '2024-03-10', 'Sold', 7),
('VEL1S12403', 1, '2024-02-02', 'Silver Metallic', 1, 750, '2024-03-12', 'Leased', 8),
('VEL2S24001', 2, '2024-02-05', 'Racing Red', 2, 300, '2024-03-18', 'Sold', 9),
('VEL2S24002', 2, '2024-02-05', 'Carbon Black', 2, 450, '2024-03-20', 'Sold', 10),

-- Completed Work Orders - Atlas Series (WorkOrder 11-12, 18)
('ATL1X12401', 11, '2024-01-20', 'Graphite Grey', 11, 800, '2024-03-01', 'Sold', 1),  -- Fleet Motors
('ATL1X12402', 11, '2024-01-21', 'Arctic White', 11, 600, '2024-03-05', 'Sold', 2),   -- Luxury Rentals
('ATL2X24001', 12, '2024-01-28', 'Ocean Blue', 12, 400, '2024-03-10', 'Leased', 3),   -- City Taxi
('ATL2X24002', 12, '2024-01-29', 'Forest Green', 12, 550, '2024-03-12', 'Sold', 4),   -- Express Delivery
('ATL4X24001', 14, '2024-02-15', 'Diamond Black', 18, 200, '2024-03-15', 'Sold', 5),  -- Corporate Fleet

-- Completed Work Orders - Horizon Series (WorkOrder 21-22)
('HOR1C12401', 21, '2024-01-25', 'Silver Sky', 21, 650, '2024-03-08', 'Sold', 11),
('HOR1C12402', 21, '2024-01-26', 'Cosmic Blue', 21, 480, '2024-03-11', 'Leased', 12),
('HOR2C24001', 22, '2024-02-01', 'Desert Sand', 22, 320, '2024-03-14', 'Sold', 13),
('HOR2C24002', 22, '2024-02-02', 'Mountain Grey', 22, 250, '2024-03-16', 'Sold', 14),

-- Completed Work Orders - Titan Series (WorkOrder 31-32)
('TIT1T12401', 31, '2024-02-01', 'Granite Black', 31, 900, '2024-03-05', 'Sold', 16),  -- Tech Transport
('TIT1T12402', 31, '2024-02-02', 'Arctic White', 31, 850, '2024-03-08', 'Sold', 17),   -- Green Fleet
('TIT2T24001', 32, '2024-02-05', 'Steel Grey', 32, 700, '2024-03-12', 'Leased', 18),   -- Regional Delivery
('TIT2T24002', 32, '2024-02-06', 'Deep Blue', 32, 600, '2024-03-15', 'Sold', 19),      -- Urban Mobility

-- Completed Work Orders - Spark Series (WorkOrder 41)
('SPK1E12401', 41, '2024-02-10', 'Electric Blue', 41, 400, '2024-03-18', 'Sold', 21),
('SPK1E12402', 41, '2024-02-11', 'Pearl White', 41, 350, '2024-03-20', 'Leased', 22),

-- In Progress Work Orders - Various Models
('VEL3S24003', 3, '2024-03-01', 'Sapphire Blue', 3, 0, NULL, 'In Production', NULL),
('VEL4S24004', 4, '2024-03-05', 'Ruby Red', 4, 0, NULL, 'In Production', NULL),
('ATL3X24003', 13, '2024-03-08', 'Emerald Green', 13, 0, NULL, 'In Production', NULL),
('HOR3C24003', 23, '2024-03-10', 'Sunset Orange', 23, 0, NULL, 'In Production', NULL),
('TIT3T24003', 33, '2024-03-12', 'Midnight Black', 33, 0, NULL, 'In Production', NULL),
('SPK2E24003', 42, '2024-03-15', 'Stellar Silver', 42, 0, NULL, 'In Production', NULL),

-- Inventory (From Recent Production)
('VEL1S24005', 1, '2024-03-18', 'Crystal White', 5, 0, NULL, 'Inventory', NULL),
('ATL1X24004', 11, '2024-03-19', 'Obsidian Black', 15, 0, NULL, 'Inventory', NULL),
('HOR1C24004', 21, '2024-03-20', 'Platinum Silver', 25, 0, NULL, 'Inventory', NULL),
('TIT1T24004', 31, '2024-03-21', 'Glacier White', 35, 0, NULL, 'Inventory', NULL),
('SPK1E24004', 41, '2024-03-22', 'Cosmic Grey', 45, 0, NULL, 'Inventory', NULL);

-- vehicle feature 


INSERT INTO VehicleFeatures (VehicleID, FeatureID) VALUES
-- Velocity S1 Base Models (VehicleIDs 1-3)
(1, 3), (1, 4), (1, 8), (1, 12), (1, 19),  -- Basic safety and comfort package
(2, 3), (2, 4), (2, 8), (2, 12), (2, 19),  -- Same base features
(3, 3), (3, 4), (3, 8), (3, 12), (3, 19),  -- Same base features

-- Velocity S2 Sport Models (VehicleIDs 4-5)
(4, 1), (4, 2), (4, 31), (4, 32), (4, 33), (4, 37),  -- Sport package
(5, 1), (5, 2), (5, 31), (5, 32), (5, 33), (5, 37),  -- Sport package

-- Atlas Series Base Models (VehicleIDs 6-7)
(6, 1), (6, 4), (6, 8), (6, 24), (6, 34),  -- SUV essentials
(7, 1), (7, 4), (7, 8), (7, 24), (7, 34),  -- SUV essentials

-- Atlas Premium Models (VehicleIDs 8-10)
(8, 1), (8, 2), (8, 3), (8, 11), (8, 12), (8, 15), (8, 21), (8, 22), (8, 23), (8, 34), -- Full premium package
(9, 1), (9, 2), (9, 3), (9, 11), (9, 12), (9, 15), (9, 21), (9, 22), (9, 23), (9, 34),
(10, 1), (10, 2), (10, 3), (10, 11), (10, 12), (10, 15), (10, 21), (10, 22), (10, 23), (10, 34),

-- Horizon Base Models (VehicleIDs 11-12)
(11, 3), (11, 4), (11, 8), (11, 34),  -- Crossover basics
(12, 3), (12, 4), (12, 8), (12, 34),  -- Crossover basics

-- Horizon Premium Models (VehicleIDs 13-14)
(13, 1), (13, 2), (13, 3), (13, 4), (13, 11), (13, 12), (13, 15),  -- Premium crossover features
(14, 1), (14, 2), (14, 3), (14, 4), (14, 11), (14, 12), (14, 15),  -- Premium crossover features

-- Titan Work Trucks (VehicleIDs 15-16)
(15, 4), (15, 8), (15, 24), (15, 34),  -- Basic work truck features
(16, 4), (16, 8), (16, 24), (16, 34),  -- Basic work truck features

-- Titan Premium Trucks (VehicleIDs 17-18)
(17, 1), (17, 2), (17, 3), (17, 4), (17, 31), (17, 32), (17, 34), (17, 35),  -- Premium truck package
(18, 1), (18, 2), (18, 3), (18, 4), (18, 31), (18, 32), (18, 34), (18, 35),  -- Premium truck package

-- Spark EV Base Models (VehicleIDs 19-20)
(19, 3), (19, 4), (19, 8), (19, 41),  -- Basic EV features
(20, 3), (20, 4), (20, 8), (20, 41),  -- Basic EV features

-- In Production Models (VehicleIDs 21-26)
(21, 1), (21, 2), (21, 3), (21, 11), (21, 12), (21, 13), (21, 14),  -- Luxury features
(22, 1), (22, 2), (22, 3), (22, 11), (22, 12), (22, 13), (22, 14),  -- Luxury features
(23, 1), (23, 2), (23, 3), (23, 11), (23, 12), (23, 15),  -- Premium features
(24, 1), (24, 2), (24, 3), (24, 11), (24, 12), (24, 15),  -- Premium features
(25, 1), (25, 2), (25, 3), (25, 31), (25, 32), (25, 33),  -- Performance features
(26, 41), (26, 42), (26, 43), (26, 44), (26, 45),  -- Full EV tech package

-- Inventory Models (VehicleIDs 27-31)
(27, 3), (27, 4), (27, 8), (27, 12), (27, 19),  -- Base sedan features
(28, 1), (28, 4), (28, 8), (28, 24), (28, 34),  -- Base SUV features
(29, 3), (29, 4), (29, 8), (29, 34),  -- Base crossover features
(30, 4), (30, 8), (30, 24), (30, 34),  -- Base truck features
(31, 3), (31, 4), (31, 8), (31, 41)   -- Base EV features


--sales order 

INSERT INTO SalesOrders (
   CustomerID, 
   OrderTimestamp, 
   ShippingAddressID, 
   Status, 
   TotalAmount
) VALUES
-- Fleet Orders (Corporate Customers)
(1, '2024-02-01 09:00:00', 105, 'Delivered', 135000.00),    -- Fleet Motors Inc
(2, '2024-02-02 10:30:00', 106, 'Delivered', 142000.00),    -- Luxury Car Rentals
(3, '2024-02-03 11:15:00', 107, 'Delivered', 168000.00),    -- City Taxi Corporation
(4, '2024-02-04 14:20:00', 108, 'Delivered', 175000.00),    -- Express Delivery Services
(5, '2024-02-05 15:45:00', 109, 'Delivered', 188000.00),    -- Corporate Fleet Solutions

-- Individual Customer Orders
(6, '2024-02-06 09:30:00', 119, 'Delivered', 32500.00),     -- Robert Anderson
(7, '2024-02-07 10:45:00', 120, 'Delivered', 32500.00),     -- Maria Garcia
(8, '2024-02-08 11:30:00', 121, 'Delivered', 32500.00),     -- James Wilson
(9, '2024-02-09 13:15:00', 122, 'Delivered', 45000.00),     -- Emily Brown
(10, '2024-02-10 14:30:00', 123, 'Delivered', 45000.00),    -- Michael Taylor

-- Additional Corporate Orders
(16, '2024-02-11 09:15:00', 130, 'Delivered', 142000.00),   -- Tech Transport Solutions
(17, '2024-02-12 10:20:00', 131, 'Delivered', 142000.00),   -- Green Fleet Services
(18, '2024-02-13 11:45:00', 132, 'Delivered', 152000.00),   -- Regional Delivery Co
(19, '2024-02-14 13:30:00', 133, 'Delivered', 152000.00),   -- Urban Mobility Group

-- Private Customer Orders
(11, '2024-02-15 15:20:00', 136, 'Delivered', 34000.00),    -- David Martinez
(12, '2024-02-16 16:30:00', 137, 'Delivered', 34000.00),    -- Sarah Johnson
(13, '2024-02-17 09:45:00', 138, 'Delivered', 42000.00),    -- Thomas Lee
(14, '2024-02-18 10:15:00', 139, 'Delivered', 42000.00),    -- Jennifer White

-- International Orders
(21, '2024-02-19 11:30:00', 139, 'Delivered', 45000.00),    -- Jean Dubois
(22, '2024-02-20 14:20:00', 139, 'Delivered', 45000.00);    -- Hans Schmidt


-- sales order items 


INSERT INTO SalesOrderItems (
   SalesOrderID, 
   VehicleID, 
   Quantity, 
   AgreedPrice
) VALUES
-- Fleet Orders Items
(1, 6, 1, 135000.00),    -- Fleet Motors buying Atlas
(2, 7, 1, 142000.00),    -- Luxury Rentals buying Atlas
(3, 8, 1, 168000.00),    -- City Taxi buying Atlas Premium
(4, 9, 1, 175000.00),    -- Express Delivery buying Atlas Premium
(5, 10, 1, 188000.00),   -- Corporate Fleet buying Atlas Elite

-- Individual Customer Items
(6, 1, 1, 32500.00),     -- Base Velocity S1
(7, 2, 1, 32500.00),     -- Base Velocity S1
(8, 3, 1, 32500.00),     -- Base Velocity S1
(9, 4, 1, 45000.00),     -- Velocity S2 Sport
(10, 5, 1, 45000.00),    -- Velocity S2 Sport

-- Additional Corporate Items
(11, 15, 1, 142000.00),  -- Titan for Tech Transport
(12, 16, 1, 142000.00),  -- Titan for Green Fleet
(13, 17, 1, 152000.00),  -- Titan Premium for Regional Delivery
(14, 18, 1, 152000.00),  -- Titan Premium for Urban Mobility

-- Private Customer Items
(15, 11, 1, 34000.00),   -- Horizon Base Model
(16, 12, 1, 34000.00),   -- Horizon Base Model
(17, 13, 1, 42000.00),   -- Horizon Premium
(18, 14, 1, 42000.00),   -- Horizon Premium

-- International Customer Items
(19, 19, 1, 45000.00),   -- Spark EV for Jean Dubois
(20, 20, 1, 45000.00);   -- Spark EV for Hans Schmidt


-- lease rental 

INSERT INTO LeaseRentalAgreements (
    CustomerID,
    VehicleID,
    AgreementType,
    StartDate,
    EndDate,
    MonthlyPayment,
    RentalRatePerDay,
    Status,
    Notes
) VALUES
-- Long-term Leases (36-month terms)
(8, 3, 'Lease', '2024-02-02', '2027-02-02', 550.00, NULL, 'Active',
    'Standard 36-month lease, Velocity S1, includes maintenance package'),
    
(3, 8, 'Lease', '2024-01-28', '2027-01-28', 850.00, NULL, 'Active',
    'Fleet lease - City Taxi Corporation, Atlas X2 Premium'),
    
(12, 12, 'Lease', '2024-01-26', '2027-01-26', 600.00, NULL, 'Active',
    'Standard 36-month lease, Horizon C1'),
    
(18, 17, 'Lease', '2024-02-05', '2027-02-05', 900.00, NULL, 'Active',
    'Commercial lease - Regional Delivery Co, Titan T2'),
    
(22, 20, 'Lease', '2024-02-11', '2027-02-11', 750.00, NULL, 'Active',
    'International lease - Spark E1, includes charging package'),

-- Short-term Rentals (Corporate)
(2, 7, 'Rental', '2024-03-01', '2024-05-01', NULL, 150.00, 'Active',
    'Corporate rental - Luxury Car Rentals'),
    
(4, 9, 'Rental', '2024-03-05', '2024-04-05', NULL, 175.00, 'Active',
    'Corporate rental - Express Delivery Services'),
    
(5, 10, 'Rental', '2024-03-10', '2024-04-10', NULL, 200.00, 'Active',
    'Corporate rental - Corporate Fleet Solutions'),

-- Short-term Rentals (Individual)
(13, 13, 'Rental', '2024-03-15', '2024-03-22', NULL, 125.00, 'Active',
    'Personal rental - Weekly'),
    
(14, 14, 'Rental', '2024-03-18', '2024-03-25', NULL, 125.00, 'Active',
    'Personal rental - Weekly');

-- service records 



INSERT INTO ServiceRecords (
    VehicleID,
    CustomerID,
    LocationID,
    TechnicianID,
    ServiceDate,
    ServiceType,
    IsWarrantyClaim,
    Notes,
    LaborHours,
    PartsCost,
    LaborCost,
    TotalCost,
    PointsEarned
) VALUES
-- Regular Maintenance Services
(1, 6, 178, 121, '2024-03-15', 'Regular Maintenance', false,
    'First service - Oil change, filters, inspection', 
    2.5, 150.00, 250.00, 400.00, 400),

(2, 7, 179, 121, '2024-03-10', 'Regular Maintenance', false,
    'First service - Oil change, filters, inspection', 
    2.5, 150.00, 250.00, 400.00, 400),

-- Warranty Claims
(3, 8, 180, 122, '2024-03-12', 'Warranty Repair', true,
    'Electronic system diagnostic and software update', 
    1.5, 0.00, 0.00, 0.00, 100),

(4, 9, 189, 122, '2024-03-18', 'Warranty Repair', true,
    'Brake system inspection and adjustment', 
    2.0, 0.00, 0.00, 0.00, 100),

-- Major Services
(6, 1, 190, 123, '2024-03-01', 'Major Service', false,
    'Fleet vehicle full service - brakes, transmission, fluids', 
    6.0, 800.00, 600.00, 1400.00, 1400),

(7, 2, 191, 123, '2024-03-05', 'Major Service', false,
    'Fleet vehicle full service - suspension, alignment, fluids', 
    5.5, 750.00, 550.00, 1300.00, 1300),

-- Repairs
(8, 3, 204, 124, '2024-03-10', 'Repair', false,
    'Replace worn brake pads and rotors', 
    3.0, 450.00, 300.00, 750.00, 750),

(9, 4, 205, 124, '2024-03-12', 'Repair', false,
    'Replace faulty oxygen sensor', 
    2.0, 300.00, 200.00, 500.00, 500),

-- Electric Vehicle Services
(19, 21, 213, 125, '2024-03-18', 'EV Service', false,
    'Battery system check and software update', 
    2.0, 100.00, 200.00, 300.00, 300),

(20, 22, 214, 125, '2024-03-20', 'EV Service', false,
    'Charging system inspection and calibration', 
    1.5, 50.00, 150.00, 200.00, 200);

-- Now insert ServicePartsUsed
INSERT INTO ServicePartsUsed (ServiceID, ComponentID, QuantityUsed, UnitPrice) VALUES
-- Regular Maintenance Parts
(1, 8, 1, 50.00),    -- Electronic control unit
(1, 33, 1, 100.00),  -- Brake system components

(2, 8, 1, 50.00),    -- Electronic control unit
(2, 33, 1, 100.00),  -- Brake system components

-- Major Service Parts
(5, 9, 1, 300.00),   -- Clutch assembly
(5, 10, 1, 500.00),  -- Gear set

(6, 32, 1, 400.00),  -- Suspension system
(6, 33, 1, 350.00),  -- Brake system

-- Repair Parts
(7, 33, 1, 450.00),  -- Brake system complete
(8, 11, 1, 300.00),  -- Engine control unit

-- EV Service Parts
(9, 14, 1, 100.00),  -- Battery management system components
(10, 14, 1, 50.00);  -- Battery management system components

-- loyalty customers 


INSERT INTO LoyaltyTransactions (
    CustomerID,
    TransactionType,
    PointsChanged,
    TransactionDate,
    RelatedServiceID,
    RelatedAgreementID,
    Notes
) VALUES
-- Points from Services
(6, 'Earned', 400, '2024-03-15', 1, NULL, 
    'Points earned from regular maintenance service'),
(7, 'Earned', 400, '2024-03-10', 2, NULL, 
    'Points earned from regular maintenance service'),
(8, 'Earned', 100, '2024-03-12', 3, NULL, 
    'Points earned from warranty service'),
(9, 'Earned', 100, '2024-03-18', 4, NULL, 
    'Points earned from warranty service'),

-- Points from Fleet Services
(1, 'Earned', 1400, '2024-03-01', 5, NULL, 
    'Points earned from fleet vehicle major service'),
(2, 'Earned', 1300, '2024-03-05', 6, NULL, 
    'Points earned from fleet vehicle major service'),
(3, 'Earned', 750, '2024-03-10', 7, NULL, 
    'Points earned from repair service'),
(4, 'Earned', 500, '2024-03-12', 8, NULL, 
    'Points earned from repair service'),

-- Points from EV Services
(21, 'Earned', 300, '2024-03-18', 9, NULL, 
    'Points earned from EV service'),
(22, 'Earned', 200, '2024-03-20', 10, NULL, 
    'Points earned from EV service'),

-- Points from Lease Agreements
(8, 'Earned', 1000, '2024-02-02', NULL, 1,
    'Sign-up bonus points for new lease agreement'),
(3, 'Earned', 2000, '2024-01-28', NULL, 2,
    'Fleet lease agreement bonus points'),
(12, 'Earned', 1000, '2024-01-26', NULL, 3,
    'Sign-up bonus points for new lease agreement'),
(18, 'Earned', 2000, '2024-02-05', NULL, 4,
    'Commercial lease agreement bonus points'),
(22, 'Earned', 1000, '2024-02-11', NULL, 5,
    'International lease agreement bonus points'),

-- Points Redemptions
(6, 'Redeemed', -500, '2024-03-20', NULL, NULL,
    'Points redeemed for service discount'),
(1, 'Redeemed', -1000, '2024-03-21', NULL, NULL,
    'Points redeemed for fleet service discount'),
(21, 'Redeemed', -200, '2024-03-22', NULL, NULL,
    'Points redeemed for EV charging credit'),

-- Welcome Bonus Points
(25, 'Earned', 500, '2024-03-15', NULL, NULL,
    'New customer welcome bonus'),
(26, 'Earned', 500, '2024-04-01', NULL, NULL,
    'New customer welcome bonus'),
(27, 'Earned', 500, '2024-04-15', NULL, NULL,
    'New customer welcome bonus'),

-- Monthly Adjustments
(1, 'Adjustment', 200, '2024-03-01', NULL, NULL,
    'Monthly fleet customer bonus'),
(2, 'Adjustment', 200, '2024-03-01', NULL, NULL,
    'Monthly fleet customer bonus'),
(3, 'Adjustment', 200, '2024-03-01', NULL, NULL,
    'Monthly fleet customer bonus'),

-- Points Expiration
(11, 'Expired', -100, '2024-03-31', NULL, NULL,
    'Points expired after 12 months'),
(12, 'Expired', -150, '2024-03-31', NULL, NULL,
    'Points expired after 12 months'),
(13, 'Expired', -75, '2024-03-31', NULL, NULL,
    'Points expired after 12 months');


-- inventory levels 

INSERT INTO InventoryLevels (
   LocationID,
   ProductID,
   ComponentID,
   QuantityOnHand,
   LastUpdated
) VALUES
-- Main Factory (Detroit - 169) Product Inventory
(169, 1, NULL, 25, '2024-03-20 09:00:00'),    -- Velocity S1
(169, 2, NULL, 20, '2024-03-20 09:00:00'),    -- Velocity S2 Sport
(169, 3, NULL, 15, '2024-03-20 09:00:00'),    -- Velocity S3
(169, 4, NULL, 10, '2024-03-20 09:00:00'),    -- Velocity S4

-- Main Factory Components Inventory
(169, NULL, 1, 50, '2024-03-20 09:00:00'),    -- V6 Engine Block
(169, NULL, 2, 30, '2024-03-20 09:00:00'),    -- V8 Engine Block
(169, NULL, 3, 100, '2024-03-20 09:00:00'),   -- Cylinder Head
(169, NULL, 4, 100, '2024-03-20 09:00:00'),   -- Crankshaft
(169, NULL, 5, 600, '2024-03-20 09:00:00'),   -- Piston Set

-- Toledo Assembly Plant (170) Product Inventory
(170, 11, NULL, 20, '2024-03-20 09:00:00'),   -- Atlas X1
(170, 12, NULL, 15, '2024-03-20 09:00:00'),   -- Atlas X2
(170, 13, NULL, 10, '2024-03-20 09:00:00'),   -- Atlas X3
(170, 14, NULL, 8, '2024-03-20 09:00:00'),    -- Atlas X4

-- Toledo Plant Components
(170, NULL, 6, 40, '2024-03-20 09:00:00'),    -- Automatic Transmission
(170, NULL, 7, 30, '2024-03-20 09:00:00'),    -- Manual Transmission
(170, NULL, 8, 80, '2024-03-20 09:00:00'),    -- Transmission Control Module
(170, NULL, 9, 60, '2024-03-20 09:00:00'),    -- Clutch Assembly
(170, NULL, 10, 100, '2024-03-20 09:00:00'),  -- Gear Set

-- Arlington Facility (171) Product Inventory
(171, 21, NULL, 18, '2024-03-20 09:00:00'),   -- Horizon C1
(171, 22, NULL, 15, '2024-03-20 09:00:00'),   -- Horizon C2
(171, 23, NULL, 12, '2024-03-20 09:00:00'),   -- Horizon C3
(171, 24, NULL, 10, '2024-03-20 09:00:00'),   -- Horizon C1 Sport

-- Arlington Components
(171, NULL, 11, 50, '2024-03-20 09:00:00'),   -- Engine Control Unit
(171, NULL, 12, 40, '2024-03-20 09:00:00'),   -- Infotainment System
(171, NULL, 13, 35, '2024-03-20 09:00:00'),   -- Digital Dashboard
(171, NULL, 14, 30, '2024-03-20 09:00:00'),   -- Battery Management System
(171, NULL, 15, 45, '2024-03-20 09:00:00'),   -- LED Headlight Assembly

-- Nashville Plant (198) Product Inventory
(198, 31, NULL, 15, '2024-03-20 09:00:00'),   -- Titan T1
(198, 32, NULL, 12, '2024-03-20 09:00:00'),   -- Titan T2
(198, 33, NULL, 10, '2024-03-20 09:00:00'),   -- Titan T3
(198, 34, NULL, 8, '2024-03-20 09:00:00'),    -- Titan T1 Work

-- Nashville Components
(198, NULL, 16, 60, '2024-03-20 09:00:00'),   -- Leather Seat Set
(198, NULL, 17, 50, '2024-03-20 09:00:00'),   -- Dashboard Assembly
(198, NULL, 18, 40, '2024-03-20 09:00:00'),   -- Climate Control Unit
(198, NULL, 19, 45, '2024-03-20 09:00:00'),   -- Door Panel Set
(198, NULL, 20, 55, '2024-03-20 09:00:00'),   -- Center Console

-- Indianapolis Plant (199) Product Inventory
(199, 41, NULL, 20, '2024-03-20 09:00:00'),   -- Spark E1
(199, 42, NULL, 15, '2024-03-20 09:00:00'),   -- Spark E2
(199, 43, NULL, 12, '2024-03-20 09:00:00'),   -- Spark E3
(199, 44, NULL, 10, '2024-03-20 09:00:00'),   -- Spark E1 Sport

-- Indianapolis EV Components
(199, NULL, 41, 40, '2024-03-20 09:00:00'),   -- Battery Pack
(199, NULL, 42, 35, '2024-03-20 09:00:00'),   -- Electric Motor
(199, NULL, 43, 25, '2024-03-20 09:00:00'),   -- Autonomous Driving Unit
(199, NULL, 44, 30, '2024-03-20 09:00:00'),   -- LiDAR Sensor
(199, NULL, 45, 35, '2024-03-20 09:00:00'),   -- Vehicle Control Module

-- Regional Warehouses Component Storage
-- Northeast Distribution Center (195)
(195, NULL, 31, 100, '2024-03-20 09:00:00'),  -- Chassis Frame
(195, NULL, 32, 80, '2024-03-20 09:00:00'),   -- Suspension System
(195, NULL, 33, 120, '2024-03-20 09:00:00'),  -- Brake System
(195, NULL, 34, 200, '2024-03-20 09:00:00'),  -- Wheel Hub Assembly
(195, NULL, 35, 150, '2024-03-20 09:00:00'),  -- Control Arms

-- Southeast Storage Hub (196)
(196, NULL, 36, 90, '2024-03-20 09:00:00'),   -- Drive Shaft
(196, NULL, 37, 75, '2024-03-20 09:00:00'),   -- Differential
(196, NULL, 38, 60, '2024-03-20 09:00:00'),   -- Transfer Case
(196, NULL, 39, 100, '2024-03-20 09:00:00'),  -- CV Joint Set
(196, NULL, 40, 85, '2024-03-20 09:00:00'),   -- Axle Assembly

-- Midwest Logistics Center (197)
(197, NULL, 46, 150, '2024-03-20 09:00:00'),  -- Steel Frame Rails
(197, NULL, 47, 120, '2024-03-20 09:00:00'),  -- Aluminum Panels
(197, NULL, 48, 80, '2024-03-20 09:00:00'),   -- Carbon Fiber Roof
(197, NULL, 49, 100, '2024-03-20 09:00:00'),  -- Polymer Dashboard Base
(197, NULL, 50, 90, '2024-03-20 09:00:00');   -- Composite Floor Pan