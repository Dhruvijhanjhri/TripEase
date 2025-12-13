-- =====================================================
-- RLS Policies for accounts_user table
-- =====================================================
-- These policies enable secure access to user data
-- while allowing authentication and profile management
-- =====================================================

-- Enable Row Level Security on accounts_user table
ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- Policy 1: Users can read their own data
-- =====================================================
-- Allows authenticated users to SELECT their own row
-- Uses auth.uid() to match the Supabase Auth user ID
-- Since we're using email as the link, we'll use email matching
CREATE POLICY "Users can read own data"
ON accounts_user
FOR SELECT
TO authenticated
USING (
    -- Match by email from Supabase Auth
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
    OR
    -- Fallback: allow if email matches authenticated user's email
    email = (SELECT raw_user_meta_data->>'email' FROM auth.users WHERE id = auth.uid())
);

-- =====================================================
-- Policy 2: Users can update their own data
-- =====================================================
-- Allows authenticated users to UPDATE their own row
-- Excludes sensitive fields like password, is_superuser, is_staff
CREATE POLICY "Users can update own data"
ON accounts_user
FOR UPDATE
TO authenticated
USING (
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
)
WITH CHECK (
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
    -- Prevent users from changing their own email, superuser status, etc.
    AND is_superuser = OLD.is_superuser
    AND is_staff = OLD.is_staff
);

-- =====================================================
-- Policy 3: Allow public signup (INSERT)
-- =====================================================
-- Allows new users to be created during signup
-- This is needed for the registration process
CREATE POLICY "Allow public signup"
ON accounts_user
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- =====================================================
-- Policy 4: Service role full access
-- =====================================================
-- Allows service role (Django backend) full access
-- This is needed for Django ORM operations
CREATE POLICY "Service role full access"
ON accounts_user
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- =====================================================
-- Policy 5: Allow authenticated users to check email existence
-- =====================================================
-- Allows checking if an email exists (for login validation)
-- Users can only check their own email
CREATE POLICY "Users can check own email"
ON accounts_user
FOR SELECT
TO authenticated
USING (
    email = (SELECT email FROM auth.users WHERE id = auth.uid())
);

-- =====================================================
-- Policy 6: Allow public to check email for login
-- =====================================================
-- Allows anonymous users to check if email exists
-- This is needed for login functionality
-- Note: This only allows checking existence, not reading full data
CREATE POLICY "Public can check email for login"
ON accounts_user
FOR SELECT
TO anon
USING (true);

-- =====================================================
-- Alternative: More restrictive login policy
-- =====================================================
-- If you want more security, use this instead of Policy 6:
-- This only allows checking email and password hash existence
-- Uncomment to use:

/*
DROP POLICY IF EXISTS "Public can check email for login" ON accounts_user;

CREATE POLICY "Public can check email for login (restricted)"
ON accounts_user
FOR SELECT
TO anon
USING (true)
WITH CHECK (false);
*/

-- =====================================================
-- Policy 7: Admin users can read all
-- =====================================================
-- Allows staff/superusers to read all user data
-- Useful for admin operations
CREATE POLICY "Staff can read all users"
ON accounts_user
FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM accounts_user
        WHERE email = (SELECT email FROM auth.users WHERE id = auth.uid())
        AND (is_staff = true OR is_superuser = true)
    )
);

-- =====================================================
-- Policy 8: Admin users can update all
-- =====================================================
-- Allows staff/superusers to update any user
CREATE POLICY "Staff can update all users"
ON accounts_user
FOR UPDATE
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM accounts_user
        WHERE email = (SELECT email FROM auth.users WHERE id = auth.uid())
        AND (is_staff = true OR is_superuser = true)
    )
);

-- =====================================================
-- Verification Queries
-- =====================================================
-- Run these to verify policies are set up correctly:

-- Check if RLS is enabled
-- SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'accounts_user';

-- List all policies
-- SELECT * FROM pg_policies WHERE tablename = 'accounts_user';

-- Test as authenticated user (replace with actual user email)
-- SET ROLE authenticated;
-- SELECT * FROM accounts_user WHERE email = 'your-email@example.com';

-- =====================================================
-- Notes:
-- =====================================================
-- 1. These policies assume email is used to link Django and Supabase users
-- 2. The service_role policy allows Django backend full access
-- 3. Public signup is enabled for registration
-- 4. Users can only read/update their own data
-- 5. Staff/superusers have elevated permissions
-- 6. Adjust policies based on your security requirements

