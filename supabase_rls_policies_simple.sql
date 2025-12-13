-- =====================================================
-- SIMPLIFIED RLS Policies for accounts_user table
-- =====================================================
-- Minimal policies for basic authentication functionality
-- =====================================================

-- Enable Row Level Security
ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can read own data" ON accounts_user;
DROP POLICY IF EXISTS "Users can update own data" ON accounts_user;
DROP POLICY IF EXISTS "Allow public signup" ON accounts_user;
DROP POLICY IF EXISTS "Service role full access" ON accounts_user;
DROP POLICY IF EXISTS "Public can check email for login" ON accounts_user;

-- =====================================================
-- Policy 1: Service role has full access
-- =====================================================
-- This is CRITICAL for Django backend operations
-- Django uses service role to manage users
CREATE POLICY "Service role full access"
ON accounts_user
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- =====================================================
-- Policy 2: Allow public signup (INSERT)
-- =====================================================
-- Allows new user registration
CREATE POLICY "Allow public signup"
ON accounts_user
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- =====================================================
-- Policy 3: Allow public to read for login
-- =====================================================
-- Allows checking email/password during login
-- This is needed for authentication
CREATE POLICY "Public can read for login"
ON accounts_user
FOR SELECT
TO anon, authenticated
USING (true);

-- =====================================================
-- Policy 4: Users can update their own profile
-- =====================================================
-- Allows users to update their own data
-- Matches by email from Supabase Auth
CREATE POLICY "Users can update own profile"
ON accounts_user
FOR UPDATE
TO authenticated
USING (
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
)
WITH CHECK (
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
);

-- =====================================================
-- That's it! These 4 policies enable:
-- =====================================================
-- ✅ Signup (INSERT)
-- ✅ Login (SELECT to check credentials)
-- ✅ Profile updates (UPDATE own data)
-- ✅ Django backend operations (service_role)
-- =====================================================

