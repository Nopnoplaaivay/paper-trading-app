CREATE SCHEMA [prmAuth]
GO

CREATE TABLE [prmAuth].[users] (
    id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    account NVARCHAR(255) UNIQUE NOT NULL, 
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) DEFAULT 'client', 
    type_broker NVARCHAR(255) NULL,
    type_client NVARCHAR(255) NULL
);