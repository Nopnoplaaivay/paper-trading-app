CREATE TABLE [Auth].[users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account] VARCHAR(255) UNIQUE NOT NULL, 
    [password] VARCHAR(255) NOT NULL,
    [role] VARCHAR(50), 
    [type_broker] VARCHAR(255) NULL,
    [type_client] VARCHAR(255) NULL,
);

GO

CREATE TABLE [Auth].[sessions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [signature] VARCHAR(255) NOT NULL, 
    [expires_at] DATETIME NOT NULL,
    [role] VARCHAR(10), 
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
    [trading_token] VARCHAR(MAX) DEFAULT '',
    [trading_token_exp] DATETIME,
    [user_id] INT NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    CONSTRAINT FK_user_accounts FOREIGN KEY (user_id) REFERENCES [Auth].[users](id) ON DELETE CASCADE
);

GO

CREATE TABLE [Investors].[transactions] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [transaction_type] VARCHAR(10),
    [amount] Integer DEFAULT 0,
    [payment_method] VARCHAR(10),
    CONSTRAINT FK_account_transactions FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);



CREATE TABLE [Investors].[securities] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [symbol] VARCHAR(10) NOT NULL,
    [price] INT NOT NULL DEFAULT 0,
    [quantity] INT NOT NULL DEFAULT 0,
    [avg_price] INT NOT NULL DEFAULT 0,
    [total_cost] INT NOT NULL DEFAULT 0,
    [total_value] INT NOT NULL DEFAULT 0,
    [realized_profit] INT DEFAULT 0,
    CONSTRAINT uq_account_symbol UNIQUE (account_id, symbol),
    CONSTRAINT fk_account FOREIGN KEY (account_id) REFERENCES [Investors].accounts(id)
);


CREATE TABLE [Orders].[orders] (
    [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID() NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] UNIQUEIDENTIFIER NOT NULL,
    [side] VARCHAR(10) NOT NULL,
    [symbol] VARCHAR(10) NOT NULL,
    [price] Integer DEFAULT 0 NOT NULL,
    [qtty] Integer DEFAULT 0 NOT NULL,
    [order_type] VARCHAR(10) NOT NULL,
    [status] VARCHAR(10) DEFAULT 'PENDING' NOT NULL,
    [error] VARCHAR(255) DEFAULT NULL,
    CONSTRAINT FK_account_orders FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);

GO

CREATE TABLE [Market_data].[stock_info] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [floor_code] VARCHAR(MAX) NOT NULL,
    [symbol] VARCHAR(MAX) NOT NULL,
    [trading_time] DATETIME,
    [security_type] VARCHAR(MAX),
    [ceiling_price] FLOAT,
    [floor_price] FLOAT,
    [highest_price] FLOAT,
    [lowest_price] FLOAT,
    [avg_price] FLOAT,
    [buy_foreign_quantity] FLOAT,
    [sell_foreign_quantity] FLOAT,
    [current_room] FLOAT,
    [accumulated_value] FLOAT,
    [accumulated_volume] FLOAT,
    [match_price] FLOAT,
    [match_quantity] FLOAT,
    [changed] FLOAT,
    [changed_ratio] FLOAT,
    [estimated_price] FLOAT,
    [trading_session] VARCHAR(MAX),
    [security_status] VARCHAR(MAX),
    [odd_lot_security_status] VARCHAR(MAX),
);

GO

CREATE TABLE [Market_data].[tick] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [symbol] VARCHAR(20) NOT NULL,
    [side] VARCHAR(9),
    [match_price] FLOAT,
    [match_quantity] FLOAT,
    [trading_time] DATETIME,
    [session] VARCHAR(20),
);

GO