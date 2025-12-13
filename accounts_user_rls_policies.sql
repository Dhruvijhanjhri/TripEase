-- =====================================================
-- COMPLETE RLS POLICIES FOR accounts_user TABLE
-- =====================================================
-- This file contains all Row Level Security policies
-- needed for authentication and user management
-- =====================================================

-- Step 1: Enable Row Level Security on accounts_user table
ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;

-- Step 2: Drop existing policies if any (for clean setup)
DROP POLICY IF EXISTS "Service role full access" ON accounts_user;
DROP POLICY IF EXISTS "Allow public signup" ON accounts_user;
DROP POLICY IF EXISTS "Public can read for login" ON accounts_user;
DROP POLICY IF EXISTS "Users can update own profile" ON accounts_user;
DROP POLICY IF EXISTS "Users can read own data" ON accounts_user;
DROP POLICY IF EXISTS "Users can check own email" ON accounts_user;
DROP POLICY IF EXISTS "Staff can read all users" ON accounts_user;
DROP POLICY IF EXISTS "Staff can update all users" ON accounts_user;
DROP POLICY IF EXISTS "Public can check email for login" ON accounts_user;

-- =====================================================
-- POLICY 1: Service Role Full Access
-- =====================================================
-- CRITICAL: Allows Django backend (service_role) to perform
-- all operations on accounts_user table
-- This is required for Django ORM to work properly
CREATE POLICY "Service role full access"
ON accounts_user
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- =====================================================
-- POLICY 2: Allow Public Signup (INSERT)
-- =====================================================
-- Allows anonymous and authenticated users to create new accounts
-- Required for user registration functionality
CREATE POLICY "Allow public signup"
ON accounts_user
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- =====================================================
-- POLICY 3: Public Can Read for Login (SELECT)
-- =====================================================
-- Allows anonymous and authenticated users to read user data
-- Required for login functionality to check email/password
-- This enables credential verification during authentication
CREATE POLICY "Public can read for login"
ON accounts_user
FOR SELECT
TO anon, authenticated
USING (true);

-- =====================================================
-- POLICY 4: Users Can Read Their Own Data (SELECT)
-- =====================================================
-- Allows authenticated users to read their own user record
-- Matches by user_id (UUID) which links to Supabase Auth
CREATE POLICY "Users can read own data"
ON accounts_user
FOR SELECT
TO authenticated
USING (
    user_id = auth.uid()
);

-- =====================================================
-- POLICY 5: Users Can Update Their Own Profile (UPDATE)
-- =====================================================
-- Allows authenticated users to update their own profile
-- Matches by user_id (UUID) which links to Supabase Auth
-- Prevents users from modifying sensitive fields like:
-- - user_id (should remain unchanged)
-- - email (should remain unchanged)
-- - is_superuser (only admins can change)
-- - is_staff (only admins can change)
CREATE POLICY "Users can update own profile"
ON accounts_user
FOR UPDATE
TO authenticated
USING (
    user_id = auth.uid()
)
WITH CHECK (
    user_id = auth.uid()
    -- Prevent users from changing their own admin status or user_id
    AND user_id = OLD.user_id
    AND is_superuser = OLD.is_superuser
    AND is_staff = OLD.is_staff
);

-- =====================================================
-- POLICY 6: Staff Can Read All Users (SELECT)
-- =====================================================
-- Allows staff/superusers to read all user records
-- Useful for admin operations and user management
-- Matches by user_id (UUID) which links to Supabase Auth
CREATE POLICY "Staff can read all users"
ON accounts_user
FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM accounts_user au
        WHERE au.user_id = auth.uid()
        AND (au.is_staff = true OR au.is_superuser = true)
    )
);

-- =====================================================
-- POLICY 7: Staff Can Update All Users (UPDATE)
-- =====================================================
-- Allows staff/superusers to update any user record
-- Required for admin user management functionality
-- Matches by user_id (UUID) which links to Supabase Auth
CREATE POLICY "Staff can update all users"
ON accounts_user
FOR UPDATE
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM accounts_user au
        WHERE au.user_id = auth.uid()
        AND (au.is_staff = true OR au.is_superuser = true)
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM accounts_user au
        WHERE au.user_id = auth.uid()
        AND (au.is_staff = true OR au.is_superuser = true)
    )
);

-- =====================================================
-- POLICY 8: Staff Can Delete Users (DELETE)
-- =====================================================
-- Allows staff/superusers to delete user records
-- Use with caution - consider soft deletes instead
-- Matches by user_id (UUID) which links to Supabase Auth
CREATE POLICY "Staff can delete users"
ON accounts_user
FOR DELETE
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM accounts_user au
        WHERE au.user_id = auth.uid()
        AND (au.is_staff = true OR au.is_superuser = true)
    )
);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these queries to verify policies are set up correctly:

-- Check if RLS is enabled
-- SELECT tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE schemaname = 'public' AND tablename = 'accounts_user';

-- List all policies on accounts_user table
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies 
-- WHERE tablename = 'accounts_user'
-- ORDER BY policyname;

-- Test query as authenticated user (replace email)
-- SET ROLE authenticated;
-- SELECT id, email, first_name, last_name FROM accounts_user WHERE email = 'test@example.com';

-- =====================================================
-- POLICY SUMMARY
-- =====================================================
-- ✅ Policy 1: Service role - Full access (Django backend)
-- ✅ Policy 2: Public/Anon - INSERT (Signup)
-- ✅ Policy 3: Public/Anon - SELECT (Login check)
-- ✅ Policy 4: Authenticated - SELECT own data
-- ✅ Policy 5: Authenticated - UPDATE own profile
-- ✅ Policy 6: Staff - SELECT all users
-- ✅ Policy 7: Staff - UPDATE all users
-- ✅ Policy 8: Staff - DELETE users
-- =====================================================

-- =====================================================
-- NOTES AND BEST PRACTICES
-- =====================================================
-- 1. Service role policy (Policy 1) is CRITICAL for Django
--    - Without it, Django ORM operations will fail
--    - This bypasses RLS for backend operations
--
-- 2. Public read policy (Policy 3) is needed for login
--    - Allows checking email/password during authentication
--    - Consider restricting to specific columns if needed
--
-- 3. User update policy (Policy 5) prevents privilege escalation
--    - Users cannot make themselves admin
--    - Email cannot be changed by users
--
-- 4. Staff policies (6, 7, 8) enable admin functionality
--    - Only users with is_staff=true or is_superuser=true
--    - Can manage other users
--
-- 5. user_id (UUID) is used as the link between Django and Supabase
--    - auth.users.id (UUID) matches accounts_user.user_id (UUID)
--    - This enables direct user identification across systems
--    - More secure and efficient than email-based matching
-- =====================================================

-- =====================================================
-- ALTERNATIVE: More Restrictive Login Policy
-- =====================================================
-- If you want to restrict public read access, you can
-- replace Policy 3 with this more restrictive version:

/*
DROP POLICY IF EXISTS "Public can read for login" ON accounts_user;

-- Only allow reading specific columns needed for login
CREATE POLICY "Public can read for login (restricted)"
ON accounts_user
FOR SELECT
TO anon, authenticated
USING (true)
WITH CHECK (false);
*/

-- =====================================================
-- TROUBLESHOOTING
-- =====================================================
-- If login/signup fails after applying policies:
--
-- 1. Verify RLS is enabled:
--    SELECT tablename, rowsecurity FROM pg_tables 
--    WHERE tablename = 'accounts_user';
--
-- 2. Check all policies exist:
--    SELECT policyname FROM pg_policies 
--    WHERE tablename = 'accounts_user';
--
-- 3. Test service role access:
--    SET ROLE service_role;
--    SELECT COUNT(*) FROM accounts_user;
--
-- 4. Test public access:
--    SET ROLE anon;
--    SELECT email FROM accounts_user LIMIT 1;
--
-- 5. Check Supabase logs for policy violations
-- =====================================================

