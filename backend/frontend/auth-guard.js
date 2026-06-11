/**
 * auth-guard.js — SalesIQ Phase 4
 * ─────────────────────────────────────────────────────────────
 * Include this script on EVERY protected page (dashboard, sales,
 * customers, products, regional, reports, etc.)
 *
 * HOW TO USE:
 *   Add this ONE line before </body> on each protected page:
 *   <script src="auth-guard.js"></script>
 *
 * ROLE RESTRICTION (optional):
 *   To restrict a page to admins only, add to <body> tag:
 *   <body data-require-role="admin">
 *
 * DYNAMIC NAV (optional):
 *   Add these data attributes anywhere in your HTML to auto-fill:
 *   data-auth-name       → shows "John Doe"
 *   data-auth-role       → shows "Administrator · Full access"
 *   data-auth-email      → shows "admin@salesiq.com"
 *   data-auth-avatar     → shows initials "JD"
 *
 * SHOW/HIDE BY ROLE:
 *   data-admin-only      → element hidden for regular users
 *   data-user-only       → element hidden for admins
 *
 * LOGOUT BUTTON:
 *   onclick="salesiqLogout()"
 * ─────────────────────────────────────────────────────────────
 */

(function () {
  'use strict';

  const API = 'http://127.0.0.1:5000/api';

  /* ════════════════════════════════════════
     1. CHECK SESSION WITH BACKEND
  ════════════════════════════════════════ */
  async function checkAuth() {
    let user = null;

    try {
      const res = await fetch(`${API}/auth/me`, {
        method      : 'GET',
        credentials : 'include'   // sends Flask session cookie
      });

      if (res.status === 401) {
        redirectToLogin();
        return;
      }

      if (!res.ok) {
        redirectToLogin();
        return;
      }

      user = await res.json();

    } catch (networkErr) {
      // Flask server offline — fall back to sessionStorage (demo mode)
      const isAuth = sessionStorage.getItem('salesiq_auth') === 'true';
      if (!isAuth) {
        redirectToLogin();
        return;
      }
      user = {
        role       : sessionStorage.getItem('salesiq_role')       || 'user',
        email      : sessionStorage.getItem('salesiq_email')      || '',
        first_name : sessionStorage.getItem('salesiq_first_name') || 'Demo',
        last_name  : sessionStorage.getItem('salesiq_last_name')  || 'User',
        user_id    : null
      };
    }

    /* ── 2. Role guard ── */
    const requiredRole = document.body.dataset.requireRole;
    if (requiredRole && user.role !== requiredRole) {
      showAccessDenied(user.role, requiredRole);
      return;
    }

    /* ── 3. Expose user globally so page scripts can use it ── */
    window.SalesIQUser = user;

    /* ── 4. Fill nav/UI with user info ── */
    injectUserInfo(user);

    /* ── 5. Show/hide role-restricted elements ── */
    applyRoleVisibility(user.role);
  }


  /* ════════════════════════════════════════
     2. REDIRECT TO LOGIN
  ════════════════════════════════════════ */
  function redirectToLogin() {
    // Remember where they were trying to go
    sessionStorage.setItem('salesiq_redirect', window.location.href);
    window.location.href = 'login.html';
  }


  /* ════════════════════════════════════════
     3. ACCESS DENIED SCREEN
  ════════════════════════════════════════ */
  function showAccessDenied(userRole, requiredRole) {
    document.body.innerHTML = `
      <div style="
        display:flex; flex-direction:column; align-items:center;
        justify-content:center; min-height:100vh;
        background:#0a0c10; color:#e8eaf0;
        font-family:'DM Sans',sans-serif; text-align:center; padding:40px;
      ">
        <div style="
          background:#181b22;
          border:1px solid rgba(245,101,101,0.3);
          border-radius:16px; padding:48px 40px; max-width:400px;
        ">
          <div style="font-size:52px; margin-bottom:16px;">🚫</div>
          <h2 style="font-size:22px; font-weight:700; margin-bottom:10px; color:#f56565;">
            Access Denied
          </h2>
          <p style="color:#7a7f8e; line-height:1.7; margin-bottom:8px;">
            This page requires
            <strong style="color:#f0a04b;">${requiredRole}</strong> access.
          </p>
          <p style="color:#7a7f8e; line-height:1.7; margin-bottom:28px;">
            You are signed in as
            <strong style="color:#4f8ef7;">${userRole}</strong>.
          </p>
          <a href="dashboard.html" style="
            display:inline-block; padding:11px 28px;
            background:#4f8ef7; color:#fff; border-radius:8px;
            text-decoration:none; font-weight:600; font-size:14px;
          ">← Back to Dashboard</a>
        </div>
      </div>
    `;
  }


  /* ════════════════════════════════════════
     4. INJECT USER INFO INTO NAV
  ════════════════════════════════════════ */
  function injectUserInfo(user) {
    const fullName  = (`${user.first_name} ${user.last_name}`).trim() || user.email;
    const roleLabel = user.role === 'admin'
      ? 'Administrator · Full access'
      : 'Sales User · View access';

    // Fill name
    document.querySelectorAll('[data-auth-name]').forEach(el => {
      el.textContent = fullName;
    });

    // Fill role label
    document.querySelectorAll('[data-auth-role]').forEach(el => {
      el.textContent = roleLabel;
    });

    // Fill email
    document.querySelectorAll('[data-auth-email]').forEach(el => {
      el.textContent = user.email;
    });

    // Fill avatar initials
    document.querySelectorAll('[data-auth-avatar]').forEach(el => {
      const initials = (
        (user.first_name?.[0] || '') +
        (user.last_name?.[0]  || '')
      ).toUpperCase();
      el.textContent = initials || 'U';
    });

    // Colour role badge
    document.querySelectorAll('[data-auth-role-badge]').forEach(el => {
      el.style.color = user.role === 'admin'
        ? 'var(--admin, #f0a04b)'
        : 'var(--accent, #4f8ef7)';
    });
  }


  /* ════════════════════════════════════════
     5. SHOW / HIDE ROLE-BASED ELEMENTS
  ════════════════════════════════════════ */
  function applyRoleVisibility(role) {
    // Only visible to admins
    document.querySelectorAll('[data-admin-only]').forEach(el => {
      el.style.display = role === 'admin' ? '' : 'none';
    });

    // Only visible to regular users
    document.querySelectorAll('[data-user-only]').forEach(el => {
      el.style.display = role === 'user' ? '' : 'none';
    });
  }


  /* ════════════════════════════════════════
     6. LOGOUT (call from nav button)
  ════════════════════════════════════════ */
  window.salesiqLogout = async function () {
    try {
      await fetch(`${API}/auth/logout`, {
        method      : 'POST',
        credentials : 'include'
      });
    } catch (_) {
      // Server offline — still clear local session
    }
    sessionStorage.clear();
    window.location.href = 'login.html';
  };


  /* ════════════════════════════════════════
     INIT
  ════════════════════════════════════════ */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuth);
  } else {
    checkAuth();
  }

})();