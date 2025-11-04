-- ArbFinder Suite - Initial Database Schema
-- PostgreSQL Migration Script v1.0
-- Description: Core schema for item tracking, pricing, and metadata management

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist"; -- For advanced indexing

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Items table - Main inventory tracking
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255),  -- ID from source platform
    source VARCHAR(50) NOT NULL,  -- shopgoodwill, govdeals, ebay, etc
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    
    -- Pricing information
    base_price DECIMAL(12, 2) NOT NULL,
    current_price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_cost DECIMAL(10, 2),
    fees DECIMAL(10, 2),
    
    -- Condition and quality
    condition VARCHAR(50),
    condition_score INTEGER CHECK (condition_score >= 0 AND condition_score <= 100),
    completeness_pct DECIMAL(5, 2) DEFAULT 100.00,
    authenticity_score INTEGER CHECK (authenticity_score >= 0 AND authenticity_score <= 100),
    
    -- Temporal data
    manufactured_date DATE,
    listed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sold_at TIMESTAMP WITH TIME ZONE,
    ends_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'sold', 'expired', 'removed', 'archived')),
    is_active BOOLEAN GENERATED ALWAYS AS (status = 'active') STORED,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    images TEXT[],
    tags TEXT[],
    
    -- Search optimization
    search_vector tsvector,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    
    CONSTRAINT items_url_unique UNIQUE (url)
);

-- Price history table - Track all price changes
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    old_price DECIMAL(12, 2),
    new_price DECIMAL(12, 2) NOT NULL,
    price_change DECIMAL(12, 2) GENERATED ALWAYS AS (new_price - old_price) STORED,
    price_change_pct DECIMAL(6, 2),
    reason VARCHAR(100),  -- market_adjustment, condition_update, manual, etc
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_by VARCHAR(100)
);

-- Comparable sales table - Historical sales data
CREATE TABLE comparable_sales (
    id SERIAL PRIMARY KEY,
    item_id UUID REFERENCES items(id) ON DELETE SET NULL,
    
    -- Item identification
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    category VARCHAR(100),
    source VARCHAR(50) NOT NULL,
    
    -- Sale information
    sale_price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    sold_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Condition at sale
    condition VARCHAR(50),
    condition_score INTEGER,
    age_at_sale DECIMAL(6, 2),  -- Years old when sold
    
    -- Market context
    market_demand_score INTEGER,
    comparable_count INTEGER DEFAULT 1,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market statistics table - Aggregated market data
CREATE TABLE market_statistics (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Aggregate metrics
    total_listings INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    avg_price DECIMAL(12, 2),
    median_price DECIMAL(12, 2),
    min_price DECIMAL(12, 2),
    max_price DECIMAL(12, 2),
    std_dev_price DECIMAL(12, 2),
    
    -- Market health
    supply_count INTEGER DEFAULT 0,
    demand_score DECIMAL(6, 2),
    sell_through_rate DECIMAL(5, 2),
    avg_days_to_sell DECIMAL(6, 2),
    
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT market_stats_unique UNIQUE (category, subcategory, period_start, period_end)
);

-- Item metadata history - Track metadata changes over time
CREATE TABLE item_metadata_history (
    id SERIAL PRIMARY KEY,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    metadata JSONB NOT NULL,
    changed_fields TEXT[] NOT NULL,
    change_summary TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_by VARCHAR(100),
    source VARCHAR(50),
    
    CONSTRAINT metadata_history_unique UNIQUE (item_id, version)
);

-- Damage assessments table - Track specific damage/defects
CREATE TABLE damage_assessments (
    id SERIAL PRIMARY KEY,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    
    -- Damage details
    damage_type VARCHAR(50) NOT NULL,  -- scratch, dent, aesthetic, structural, rust, etc
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('minor', 'moderate', 'major', 'severe')),
    location VARCHAR(100),  -- "passenger door", "top left corner", etc
    description TEXT,
    
    -- Impact on price
    estimated_impact_pct DECIMAL(6, 2) NOT NULL,
    applied_adjustment DECIMAL(12, 2),
    
    -- Evidence
    image_urls TEXT[],
    detected_by VARCHAR(50),  -- manual, cv_model, user_report
    confidence DECIMAL(5, 2),  -- For automated detection
    
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assessed_by VARCHAR(100)
);

-- Depreciation models table - Store depreciation curves
CREATE TABLE depreciation_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100),
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('linear', 'exponential', 's_curve', 'custom')),
    
    -- Model parameters
    parameters JSONB NOT NULL,
    -- Example: {"rate": 0.10} for linear
    --          {"half_life_years": 2.5} for exponential
    
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Price adjustments table - Record all adjustments applied
CREATE TABLE price_adjustments (
    id SERIAL PRIMARY KEY,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    
    adjustment_type VARCHAR(50) NOT NULL,  -- depreciation, condition, damage, market, seasonal
    adjustment_factor DECIMAL(8, 4) NOT NULL,  -- Multiplier or percentage
    adjustment_amount DECIMAL(12, 2),
    
    -- Context
    reason TEXT NOT NULL,
    calculation_details JSONB,
    
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100)
);

-- User watchlists table - Track items users are monitoring
CREATE TABLE user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    
    -- Notification preferences
    notify_on_price_drop BOOLEAN DEFAULT true,
    notify_on_price_threshold DECIMAL(12, 2),
    notify_on_status_change BOOLEAN DEFAULT true,
    
    notes TEXT,
    
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT watchlist_unique UNIQUE (user_id, item_id)
);

-- Search queries table - Track what users search for
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    user_id VARCHAR(100),
    
    -- Results
    results_count INTEGER,
    avg_price DECIMAL(12, 2),
    
    -- Context
    filters JSONB,
    
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    search_duration_ms INTEGER
);

-- Data ingestion log - Track scraping and data import
CREATE TABLE data_ingestion_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    ingestion_type VARCHAR(50) NOT NULL,  -- scrape, import, api, manual
    
    -- Stats
    items_processed INTEGER DEFAULT 0,
    items_created INTEGER DEFAULT 0,
    items_updated INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'running', 'completed', 'failed')),
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Items table indexes
CREATE INDEX idx_items_source ON items(source);
CREATE INDEX idx_items_status ON items(status) WHERE status = 'active';
CREATE INDEX idx_items_category ON items(category, subcategory);
CREATE INDEX idx_items_price ON items(current_price) WHERE is_active;
CREATE INDEX idx_items_listed_at ON items(listed_at DESC);
CREATE INDEX idx_items_sold_at ON items(sold_at) WHERE sold_at IS NOT NULL;
CREATE INDEX idx_items_search_vector ON items USING GIN(search_vector);
CREATE INDEX idx_items_metadata ON items USING GIN(metadata);
CREATE INDEX idx_items_tags ON items USING GIN(tags);

-- Composite indexes for common queries
CREATE INDEX idx_items_active_category_price ON items(category, current_price DESC) 
    WHERE status = 'active';
CREATE INDEX idx_items_source_listed ON items(source, listed_at DESC);

-- Full-text search optimization
CREATE INDEX idx_items_title_trgm ON items USING GIN(title gin_trgm_ops);
CREATE INDEX idx_items_description_trgm ON items USING GIN(description gin_trgm_ops);

-- Price history indexes
CREATE INDEX idx_price_history_item_id ON price_history(item_id, changed_at DESC);
CREATE INDEX idx_price_history_changed_at ON price_history(changed_at DESC);

-- Comparable sales indexes
CREATE INDEX idx_comparable_sales_title_trgm ON comparable_sales USING GIN(normalized_title gin_trgm_ops);
CREATE INDEX idx_comparable_sales_category ON comparable_sales(category, sold_at DESC);
CREATE INDEX idx_comparable_sales_sold_at ON comparable_sales(sold_at DESC);
CREATE INDEX idx_comparable_sales_price ON comparable_sales(sale_price);

-- Market statistics indexes
CREATE INDEX idx_market_stats_category ON market_statistics(category, period_start DESC);
CREATE INDEX idx_market_stats_period ON market_statistics(period_start, period_end);

-- Metadata history indexes
CREATE INDEX idx_metadata_history_item_id ON item_metadata_history(item_id, version DESC);
CREATE INDEX idx_metadata_history_changed_at ON item_metadata_history(changed_at DESC);

-- Damage assessments indexes
CREATE INDEX idx_damage_assessments_item_id ON damage_assessments(item_id);
CREATE INDEX idx_damage_assessments_type ON damage_assessments(damage_type, severity);

-- Price adjustments indexes
CREATE INDEX idx_price_adjustments_item_id ON price_adjustments(item_id, applied_at DESC);
CREATE INDEX idx_price_adjustments_type ON price_adjustments(adjustment_type);

-- User watchlists indexes
CREATE INDEX idx_user_watchlists_user_id ON user_watchlists(user_id, added_at DESC);
CREATE INDEX idx_user_watchlists_item_id ON user_watchlists(item_id);

-- Search queries indexes
CREATE INDEX idx_search_queries_normalized ON search_queries(normalized_query, searched_at DESC);
CREATE INDEX idx_search_queries_user_id ON search_queries(user_id, searched_at DESC);

-- Data ingestion log indexes
CREATE INDEX idx_data_ingestion_source ON data_ingestion_log(source, started_at DESC);
CREATE INDEX idx_data_ingestion_status ON data_ingestion_log(status, started_at DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply timestamp trigger to items
CREATE TRIGGER trigger_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply timestamp trigger to depreciation models
CREATE TRIGGER trigger_depreciation_models_updated_at
    BEFORE UPDATE ON depreciation_models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger function to update search vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply search vector trigger
CREATE TRIGGER trigger_items_search_vector
    BEFORE INSERT OR UPDATE OF title, description, category ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- Trigger function to log price changes
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.current_price IS DISTINCT FROM NEW.current_price THEN
        INSERT INTO price_history (item_id, old_price, new_price, price_change_pct, reason)
        VALUES (
            NEW.id,
            OLD.current_price,
            NEW.current_price,
            CASE 
                WHEN OLD.current_price > 0 THEN 
                    ((NEW.current_price - OLD.current_price) / OLD.current_price) * 100
                ELSE NULL
            END,
            'automatic'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply price change logging trigger
CREATE TRIGGER trigger_items_log_price_change
    AFTER UPDATE OF current_price ON items
    FOR EACH ROW
    EXECUTE FUNCTION log_price_change();

-- Trigger function to track metadata changes
CREATE OR REPLACE FUNCTION log_metadata_change()
RETURNS TRIGGER AS $$
DECLARE
    version_num INTEGER;
    changed_keys TEXT[];
BEGIN
    IF OLD.metadata IS DISTINCT FROM NEW.metadata THEN
        -- Get next version number
        SELECT COALESCE(MAX(version), 0) + 1 INTO version_num
        FROM item_metadata_history
        WHERE item_id = NEW.id;
        
        -- Find changed fields (simplified - tracks top-level keys only)
        SELECT ARRAY_AGG(key)
        INTO changed_keys
        FROM jsonb_object_keys(NEW.metadata) AS key
        WHERE NEW.metadata->key IS DISTINCT FROM OLD.metadata->key;
        
        -- Insert history record
        INSERT INTO item_metadata_history (
            item_id, version, metadata, changed_fields, source
        ) VALUES (
            NEW.id,
            version_num,
            NEW.metadata,
            COALESCE(changed_keys, ARRAY['initial']),
            'trigger'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply metadata change logging trigger
CREATE TRIGGER trigger_items_log_metadata_change
    AFTER UPDATE OF metadata ON items
    FOR EACH ROW
    EXECUTE FUNCTION log_metadata_change();

-- Trigger function to auto-archive old items
CREATE OR REPLACE FUNCTION auto_archive_old_items()
RETURNS TRIGGER AS $$
BEGIN
    -- Archive items that have been sold or expired for over 90 days
    IF NEW.status IN ('sold', 'expired') AND 
       NEW.updated_at < NOW() - INTERVAL '90 days' AND
       OLD.status != 'archived' THEN
        NEW.status := 'archived';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply auto-archive trigger
CREATE TRIGGER trigger_items_auto_archive
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION auto_archive_old_items();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active items with calculated metrics
CREATE OR REPLACE VIEW v_active_items_metrics AS
SELECT 
    i.id,
    i.title,
    i.category,
    i.current_price,
    i.condition,
    i.condition_score,
    
    -- Age calculation
    EXTRACT(YEAR FROM AGE(NOW(), i.manufactured_date)) AS age_years,
    
    -- Days listed
    EXTRACT(DAY FROM AGE(NOW(), i.listed_at)) AS days_listed,
    
    -- Price metrics
    (SELECT AVG(new_price) FROM price_history WHERE item_id = i.id) AS avg_historical_price,
    (SELECT COUNT(*) FROM price_history WHERE item_id = i.id) AS price_change_count,
    
    -- Market comparison
    (
        SELECT AVG(cs.sale_price)
        FROM comparable_sales cs
        WHERE cs.category = i.category
        AND cs.sold_at > NOW() - INTERVAL '30 days'
    ) AS avg_category_sale_price,
    
    i.listed_at,
    i.source
FROM items i
WHERE i.status = 'active';

-- Market trends view
CREATE OR REPLACE VIEW v_market_trends AS
SELECT 
    category,
    subcategory,
    COUNT(*) AS total_items,
    AVG(current_price) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) AS median_price,
    MIN(current_price) AS min_price,
    MAX(current_price) AS max_price,
    STDDEV(current_price) AS price_std_dev,
    AVG(condition_score) AS avg_condition,
    COUNT(*) FILTER (WHERE listed_at > NOW() - INTERVAL '7 days') AS new_last_week
FROM items
WHERE status = 'active'
GROUP BY category, subcategory;

-- Price performance view
CREATE OR REPLACE VIEW v_price_performance AS
SELECT 
    i.id,
    i.title,
    i.base_price,
    i.current_price,
    i.base_price - i.current_price AS total_discount,
    CASE 
        WHEN i.base_price > 0 THEN 
            ((i.base_price - i.current_price) / i.base_price) * 100
        ELSE 0
    END AS discount_pct,
    (SELECT COUNT(*) FROM price_history WHERE item_id = i.id) AS adjustments_count,
    (
        SELECT STRING_AGG(adjustment_type, ', ')
        FROM price_adjustments
        WHERE item_id = i.id
    ) AS adjustment_types,
    i.status,
    i.listed_at
FROM items i;

-- ============================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================================

-- Function to calculate depreciation
CREATE OR REPLACE FUNCTION calculate_depreciation(
    p_base_price DECIMAL,
    p_age_years DECIMAL,
    p_model_type VARCHAR,
    p_parameters JSONB
)
RETURNS DECIMAL AS $$
DECLARE
    depreciation_factor DECIMAL;
    rate DECIMAL;
    half_life DECIMAL;
BEGIN
    CASE p_model_type
        WHEN 'linear' THEN
            rate := (p_parameters->>'rate')::DECIMAL;
            depreciation_factor := 1 - (p_age_years * rate);
            
        WHEN 'exponential' THEN
            half_life := (p_parameters->>'half_life_years')::DECIMAL;
            depreciation_factor := POWER(0.5, p_age_years / half_life);
            
        WHEN 's_curve' THEN
            -- Simplified S-curve implementation
            IF p_age_years < 1 THEN
                depreciation_factor := 0.7 + (0.3 * (1 - p_age_years));
            ELSIF p_age_years < 5 THEN
                depreciation_factor := 0.6 + (0.1 * (5 - p_age_years) / 4);
            ELSE
                depreciation_factor := 0.5;
            END IF;
            
        ELSE
            depreciation_factor := 1.0;
    END CASE;
    
    -- Ensure factor is between 0 and 1
    depreciation_factor := GREATEST(0.0, LEAST(1.0, depreciation_factor));
    
    RETURN p_base_price * depreciation_factor;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get condition multiplier
CREATE OR REPLACE FUNCTION get_condition_multiplier(p_condition VARCHAR)
RETURNS DECIMAL AS $$
BEGIN
    RETURN CASE p_condition
        WHEN 'new' THEN 1.00
        WHEN 'like_new' THEN 0.95
        WHEN 'excellent' THEN 0.85
        WHEN 'very_good' THEN 0.75
        WHEN 'good' THEN 0.65
        WHEN 'fair' THEN 0.50
        WHEN 'poor' THEN 0.30
        ELSE 0.75  -- Default
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to normalize item title for comparison
CREATE OR REPLACE FUNCTION normalize_title(p_title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(p_title, '[^a-zA-Z0-9\s]', '', 'g'),
            '\s+', ' ', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Materialized view for category statistics (refreshed periodically)
CREATE MATERIALIZED VIEW mv_category_statistics AS
SELECT 
    category,
    subcategory,
    COUNT(*) AS item_count,
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'sold') AS sold_count,
    AVG(current_price) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) AS median_price,
    AVG(condition_score) AS avg_condition_score,
    AVG(EXTRACT(DAY FROM AGE(COALESCE(sold_at, NOW()), listed_at))) AS avg_days_to_sell,
    MAX(updated_at) AS last_updated
FROM items
WHERE category IS NOT NULL
GROUP BY category, subcategory;

-- Create unique index on materialized view
CREATE UNIQUE INDEX idx_mv_category_stats_unique 
ON mv_category_statistics(category, COALESCE(subcategory, ''));

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default depreciation models
INSERT INTO depreciation_models (name, category, model_type, parameters, description) VALUES
('Electronics - Linear', 'Electronics', 'linear', '{"rate": 0.15}', '15% per year linear depreciation for electronics'),
('Electronics - Exponential', 'Electronics', 'exponential', '{"half_life_years": 2.5}', 'Exponential decay with 2.5 year half-life'),
('Vehicles - Linear', 'Vehicles', 'linear', '{"rate": 0.10}', '10% per year linear depreciation for vehicles'),
('Collectibles - S-Curve', 'Collectibles', 's_curve', '{}', 'S-curve appreciation for collectibles'),
('General - Linear', NULL, 'linear', '{"rate": 0.12}', 'General purpose 12% annual depreciation');

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE items IS 'Main table for tracking all items across platforms';
COMMENT ON TABLE price_history IS 'Audit log of all price changes for items';
COMMENT ON TABLE comparable_sales IS 'Historical sales data for market analysis';
COMMENT ON TABLE market_statistics IS 'Aggregated market metrics by category and time period';
COMMENT ON TABLE item_metadata_history IS 'Version control for item metadata changes';
COMMENT ON TABLE damage_assessments IS 'Detailed tracking of item damage and defects';
COMMENT ON TABLE depreciation_models IS 'Configurable depreciation calculation models';
COMMENT ON TABLE price_adjustments IS 'Audit log of all price adjustment calculations';

COMMENT ON COLUMN items.search_vector IS 'Full-text search vector for efficient searching';
COMMENT ON COLUMN items.is_active IS 'Generated column for quick active item filtering';
COMMENT ON COLUMN price_history.price_change_pct IS 'Percentage change from old to new price';
COMMENT ON COLUMN damage_assessments.confidence IS 'Confidence score for automated damage detection';

-- ============================================================================
-- GRANTS (adjust as needed for your environment)
-- ============================================================================

-- Example grants for application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arbfinder_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arbfinder_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO arbfinder_app;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- To refresh materialized views (run periodically via cron or scheduler)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_statistics;

-- To analyze tables for query optimization (run after bulk inserts)
-- ANALYZE items;
-- ANALYZE price_history;
-- ANALYZE comparable_sales;

COMMIT;
