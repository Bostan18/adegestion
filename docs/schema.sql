-- AdeImmo, schéma initial de base de données
-- Base de données : Supabase (PostgreSQL)

-- Utilisateurs (agents de l'agence)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'agent', 'comptable')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Biens immobiliers
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('appartement', 'villa', 'terrain', 'bureau', 'commerce')),
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    surface_m2 NUMERIC,
    rent_amount NUMERIC NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('disponible', 'loue', 'en_travaux', 'indisponible')),
    owner_name TEXT,
    owner_contact TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Photos des biens (un bien peut avoir plusieurs photos)
CREATE TABLE property_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    is_cover BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Baux
CREATE TABLE leases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    tenant_name TEXT NOT NULL,
    tenant_contact TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    rent_amount NUMERIC NOT NULL,
    deposit_amount NUMERIC,
    status TEXT NOT NULL CHECK (status IN ('actif', 'termine', 'resilie')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Paiements (loyers et quittances)
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lease_id UUID NOT NULL REFERENCES leases(id),
    amount NUMERIC NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN (
        'especes', 'virement_bancaire', 'cheque', 'mobile_money_orange',
        'mobile_money_mtn', 'mobile_money_moov', 'wave'
    )),
    reference_number TEXT,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    -- Echeance du loyer, toujours connue.
    due_date DATE NOT NULL,
    -- Date d'encaissement effectif, vide tant que le paiement n'est pas abouti
    -- (cheque remis non credite, virement annonce).
    paid_at DATE,
    status TEXT NOT NULL CHECK (status IN ('paye', 'en_attente', 'en_retard', 'rejete')),
    receipt_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT payments_paid_at_required_check
        CHECK (status <> 'paye' OR paid_at IS NOT NULL)
);

-- Tickets de maintenance
CREATE TABLE maintenance_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    reported_by UUID REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL CHECK (priority IN ('basse', 'moyenne', 'haute', 'urgente')),
    status TEXT NOT NULL CHECK (status IN ('ouvert', 'en_cours', 'resolu', 'ferme')),
    created_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

-- Index utiles
CREATE INDEX idx_leases_property_id ON leases(property_id);
CREATE INDEX idx_payments_lease_id ON payments(lease_id);
CREATE INDEX idx_maintenance_property_id ON maintenance_tickets(property_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_due_date ON payments(due_date);
