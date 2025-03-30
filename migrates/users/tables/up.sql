use KVSecurities;

CREATE SCHEMA [KVS_AUTH];
GO

CREATE SCHEMA [KVS_ACCOUNTS];
GO

CREATE SCHEMA [KVS_ORDERS];
GO

CREATE TABLE [KVS_AUTH].[users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [account] NVARCHAR(255) UNIQUE NOT NULL, 
    [password] NVARCHAR(255) NOT NULL,
    [role] NVARCHAR(50), 
    [type_broker] NVARCHAR(255) NULL,
    [type_client] NVARCHAR(255) NULL,
);

CREATE TABLE [KVS_AUTH].[sessions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [created_at] DATETIME NOT NULL,
    [updated_at] DATETIME NOT NULL,
    [signature] NVARCHAR(255) NOT NULL, 
    [expires_at] DATETIME NOT NULL,
    [role] NVARCHAR(10), 
    [user_id] INT NOT NULL,
    CONSTRAINT FK_user_sessions FOREIGN KEY (user_id) REFERENCES [KVS_AUTH].[users](id) ON DELETE CASCADE
);

CREATE TABLE [KVS_ACCOUNTS].[accounts] (
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
    CONSTRAINT FK_user_accounts FOREIGN KEY (user_id) REFERENCES [KVS_AUTH].[users](id) ON DELETE CASCADE
);

CREATE TABLE [KVS_ACCOUNTS].[transactions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [transaction_type] NVARCHAR(10),
    [amount] Integer DEFAULT 0,
    [payment_method] NVARCHAR(10),
    [created_at] DATETIME NOT NULL,
    CONSTRAINT FK_account_transactions FOREIGN KEY (account_id) REFERENCES [KVS_ACCOUNTS].[accounts](id)
);

CREATE TABLE [KVS_ORDERS].[orders] (
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
    CONSTRAINT FK_account_orders FOREIGN KEY (account_id) REFERENCES [KVS_ACCOUNTS].[accounts](id)
);