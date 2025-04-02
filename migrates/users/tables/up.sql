USE KVSecurities;

GO

CREATE SCHEMA [Auth];
GO

CREATE SCHEMA [Investors];
GO

CREATE SCHEMA [Orders];
GO

CREATE SCHEMA [Market_data];
GO

CREATE TABLE [Auth].[users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [account] NVARCHAR(255) UNIQUE NOT NULL, 
    [password] NVARCHAR(255) NOT NULL,
    [role] NVARCHAR(50), 
    [type_broker] NVARCHAR(255) NULL,
    [type_client] NVARCHAR(255) NULL
);

GO

CREATE TABLE [Auth].[sessions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [created_at] DATETIME NOT NULL,
    [updated_at] DATETIME NOT NULL,
    [signature] NVARCHAR(255) NOT NULL, 
    [expires_at] DATETIME NOT NULL,
    [role] NVARCHAR(10), 
    [user_id] INT NOT NULL,
    CONSTRAINT FK_user_sessions FOREIGN KEY (user_id) REFERENCES [Auth].[users](id) ON DELETE CASCADE
);

GO

CREATE TABLE [Investors].[accounts] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [total_cash] Integer DEFAULT 0,
    [available_cash] Integer DEFAULT 0,
    [withdrawable_cash] Integer DEFAULT 0,
    [stock_value] Integer DEFAULT 0,
    [total_debt] Integer DEFAULT 0,
    [net_asset_value] Integer DEFAULT 0,
    [securing_amount] Integer DEFAULT 0,
    [receiving_amount] Integer DEFAULT 0,
    [purchasing_power] Integer DEFAULT 0,
    [trading_token] NVARCHAR(MAX) DEFAULT '',
    [trading_token_exp] DATETIME,
    [user_id] INT NOT NULL,
    CONSTRAINT FK_user_accounts FOREIGN KEY (user_id) REFERENCES [Auth].[users](id) ON DELETE CASCADE
);

GO

CREATE TABLE [Investors].[transactions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [transaction_type] NVARCHAR(10),
    [amount] Integer DEFAULT 0,
    [payment_method] NVARCHAR(10),
    [created_at] DATETIME NOT NULL,
    CONSTRAINT FK_account_transactions FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);

GO

CREATE TABLE [Orders].[orders] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [side] NVARCHAR(10) NOT NULL,
    [symbol] NVARCHAR(10) NOT NULL,
    [price] Integer DEFAULT 0 NOT NULL,
    [order_quantity] Integer DEFAULT 0 NOT NULL,
    [order_type] NVARCHAR(10) NOT NULL,
    [order_status] NVARCHAR(10) DEFAULT 'PENDING' NOT NULL,
    [filled_quantity] Integer DEFAULT 0,
    [last_quantity] Integer DEFAULT 0,
    [error] NVARCHAR(255) DEFAULT NULL,
    [created_at] DATETIME NOT NULL,
    [updated_at] DATETIME NOT NULL,
    CONSTRAINT FK_account_orders FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);

GO

CREATE TABLE [Market_data].[stock_info] (
    id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    floor_code NVARCHAR(MAX) NOT NULL,
    symbol NVARCHAR(MAX) NOT NULL,
    trading_time DATETIME NULL,
    security_type NVARCHAR(MAX) NULL,
    ceiling_price FLOAT NULL,
    floor_price FLOAT NULL,
    highest_price FLOAT NULL,
    lowest_price FLOAT NULL,
    avg_price FLOAT NULL,
    buy_foreign_quantity FLOAT NULL,
    sell_foreign_quantity FLOAT NULL,
    current_room FLOAT NULL,
    accumulated_value FLOAT NULL,
    accumulated_volume FLOAT NULL,
    match_price FLOAT NULL,
    match_quantity FLOAT NULL,
    changed FLOAT NULL,
    changed_ratio FLOAT NULL,
    estimated_price FLOAT NULL,
    trading_session NVARCHAR(MAX) NULL,
    security_status NVARCHAR(MAX) NULL,
    odd_lot_security_status NVARCHAR(MAX) NULL
);

GO

CREATE TABLE [Market_data].[tick] (
    id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    symbol NVARCHAR(20) NOT NULL,
    side NVARCHAR(9) NULL,
    match_price FLOAT NULL,
    match_quantity FLOAT NULL,
    trading_time DATETIME,
    session NVARCHAR(20) NULL
);

GO