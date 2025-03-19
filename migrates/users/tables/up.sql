CREATE SCHEMA [prmAuth]
GO

CREATE TABLE [prmAuth].[users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [account] NVARCHAR(255) UNIQUE NOT NULL, 
    [password] NVARCHAR(255) NOT NULL,
    [role] NVARCHAR(50), 
    [type_broker] NVARCHAR(255) NULL,
    [type_client] NVARCHAR(255) NULL
);

CREATE TABLE [prmAuth].[sessions] (
    [id] INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    [signature] NVARCHAR(255) NOT NULL, 
    [expires_at] DATETIME NOT NULL,
    [role] NVARCHAR(50), 
    [user_id] INT NOT NULL,
    CONSTRAINT FK_user_sessions FOREIGN KEY (user_id) REFERENCES [prmAuth].[users](id) ON DELETE CASCADE
);