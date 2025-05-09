CREATE TABLE [Auth].[users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account] VARCHAR(255) UNIQUE NOT NULL, 
    [password] VARCHAR(255) NOT NULL,
    [role] VARCHAR(50)
);

GO

CREATE TABLE [Auth].[sessions] (
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
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
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
    [available_cash] Integer DEFAULT 0,
    [securing_amount] Integer DEFAULT 0,
    [purchasing_power] Integer DEFAULT 0,
    [user_id] INT NOT NULL,
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    CONSTRAINT FK_user_accounts FOREIGN KEY (user_id) REFERENCES [Auth].[users](id) ON DELETE CASCADE
);

GO

CREATE TABLE [Investors].[transactions] (
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] VARCHAR(36) NOT NULL,
    [transaction_type] VARCHAR(10),
    [amount] Integer DEFAULT 0,
    [payment_method] VARCHAR(10),
    CONSTRAINT FK_account_transactions FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);


CREATE TABLE [Investors].[holdings] (
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] VARCHAR(36) NOT NULL,
    [symbol] VARCHAR(10) NOT NULL,
    [price] INT NOT NULL DEFAULT 0,
    [quantity] INT NOT NULL DEFAULT 0,
    [locked_quantity] INT NOT NULL DEFAULT 0,
    [cost_basis_per_share] INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_account_symbol UNIQUE (account_id, symbol),
    CONSTRAINT fk_account FOREIGN KEY (account_id) REFERENCES [Investors].accounts(id)
);


CREATE TABLE [Orders].[orders] (
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] VARCHAR(36) NOT NULL,
    [side] VARCHAR(10) NOT NULL,
    [symbol] VARCHAR(10) NOT NULL,
    [price] Integer DEFAULT 0 NOT NULL,
    [quantity] Integer DEFAULT 0 NOT NULL,
    [order_type] VARCHAR(10) NOT NULL,
    [status] VARCHAR(10) DEFAULT 'PENDING' NOT NULL,
    [error] VARCHAR(255) DEFAULT NULL,
    CONSTRAINT FK_account_orders FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
);

GO

CREATE TABLE [Orders].[match_orders] (
    [id] VARCHAR(36) PRIMARY KEY DEFAULT (LOWER(NEWID())),
    [__created_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [__updated_at__] VARCHAR(19) default (format(switchoffset(sysutcdatetime(),'+07:00'),'yyyy-MM-dd HH:mm:ss')) NOT NULL,
    [account_id] VARCHAR(36) NOT NULL,
    [order_id] VARCHAR(36) NOT NULL,
    [side] VARCHAR(10) NOT NULL,
    [symbol] VARCHAR(10) NOT NULL,
    [price] Integer DEFAULT 0 NOT NULL,
    [quantity] Integer DEFAULT 0 NOT NULL,
    [total_amount] Integer DEFAULT 0 NOT NULL,
    [order_type] VARCHAR(10) NOT NULL,
    CONSTRAINT FK_account_match_orders FOREIGN KEY (account_id) REFERENCES [Investors].[accounts](id)
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