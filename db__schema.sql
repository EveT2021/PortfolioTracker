-- ============================================
-- ENUM for transaction types (space efficient)
-- ============================================
CREATE TYPE transaction_type AS ENUM (
    'buy', 
    'sell', 
    'dividend', 
    'split', 
    'transfer_in', 
    'transfer_out',
    'fee'
);

-- ============================================
-- USERS
-- ============================================
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   CHAR(60) NOT NULL,          -- bcrypt = 60 chars
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT email_format CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')
);

-- ============================================
-- ASSET TYPES (dynamically extensible)
-- ============================================
-- Add new rows to support new asset classes without schema changes
CREATE TABLE asset_types (
    id              SMALLSERIAL PRIMARY KEY,    -- SMALLINT saves space
    name            VARCHAR(50) NOT NULL UNIQUE,
    description     TEXT,
    schema_hint     JSONB                       -- documents expected metadata fields
);

-- Seed with common types
INSERT INTO asset_types (name, description, schema_hint) VALUES
    ('stock', 'Public equities', '{"required": ["ticker", "exchange"], "optional": ["sector", "isin"]}'),
    ('etf', 'Exchange-traded funds', '{"required": ["ticker", "exchange"], "optional": ["expense_ratio"]}'),
    ('crypto', 'Cryptocurrency', '{"required": ["symbol"], "optional": ["chain", "contract_address"]}'),
    ('bond', 'Fixed income', '{"required": ["coupon_rate", "maturity_date"], "optional": ["credit_rating"]}'),
    ('cash', 'Cash and equivalents', '{"required": ["currency"]}'),
    ('real_estate', 'Property', '{"required": ["address"], "optional": ["sq_ft", "property_type"]}');

-- ============================================
-- ASSETS (the securities/instruments)
-- ============================================
CREATE TABLE assets (
    id              SERIAL PRIMARY KEY,
    type_id         SMALLINT NOT NULL REFERENCES asset_types(id),
    name            VARCHAR(255) NOT NULL,
    symbol          VARCHAR(20),                -- nullable: not all assets have symbols
    metadata        JSONB DEFAULT '{}',         -- type-specific attributes
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW() ON UPDATE NOW(),
    
    CONSTRAINT unique_symbol_per_type UNIQUE (type_id, symbol),
    CONSTRAINT chk_symbol CHECK (symbol IS NULL OR symbol <> '')
);

-- Index for fast lookups by symbol
CREATE INDEX idx_assets_symbol ON assets(symbol) WHERE symbol IS NOT NULL;
CREATE INDEX idx_assets_metadata ON assets USING GIN(metadata);

-- ============================================
-- PORTFOLIOS
-- ============================================
CREATE TABLE portfolios (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_portfolio_name_per_user UNIQUE (user_id, name)
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

-- ============================================
-- HOLDINGS (current state - denormalized for read efficiency)
-- ============================================
CREATE TABLE holdings (
    portfolio_id    INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id        INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    quantity        DECIMAL(18, 8) NOT NULL,    -- 8 decimals for crypto precision
    cost_basis      DECIMAL(14, 2) NOT NULL,    -- total cost in base currency
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (portfolio_id, asset_id),       -- composite PK, no separate id needed
    CONSTRAINT positive_quantity CHECK (quantity >= 0)
);

-- ============================================
-- TRANSACTIONS (immutable ledger)
-- ============================================
CREATE TABLE transactions (
    id              BIGSERIAL PRIMARY KEY,      -- BIGINT for high volume
    portfolio_id    INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id        INTEGER NOT NULL REFERENCES assets(id),
    type            transaction_type NOT NULL,
    quantity        DECIMAL(18, 8) NOT NULL,    -- can be negative for sells
    price_per_unit  DECIMAL(14, 6),             -- nullable for transfers
    total_amount    DECIMAL(14, 2),             -- total value of transaction
    fees            DECIMAL(10, 2) DEFAULT 0,
    executed_at     TIMESTAMPTZ NOT NULL,       -- when trade actually happened
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()   -- when record was created
);

-- Indexes for common query patterns
CREATE INDEX idx_txn_portfolio ON transactions(portfolio_id);
CREATE INDEX idx_txn_portfolio_date ON transactions(portfolio_id, executed_at DESC);
CREATE INDEX idx_txn_asset ON transactions(asset_id);