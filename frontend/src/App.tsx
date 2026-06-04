import { Routes, Route } from 'react-router-dom'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardLayout } from './components/layout/DashboardLayout'
import { DashboardPage } from './pages/DashboardPage'
import { PropertiesPage } from './pages/PropertiesPage'
import { AddPropertyPage } from './pages/AddPropertyPage'
import { PropertyDetailPage } from './pages/PropertyDetailPage'
import { ComparePage } from './pages/ComparePage'
import { RankingsPage } from './pages/RankingsPage'
import { ReportsPage } from './pages/ReportsPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { AdminSettingsPage } from './pages/AdminSettingsPage'
import { ProtectedRoute, GuestRoute } from './components/auth/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/login"
        element={
          <GuestRoute>
            <LoginPage />
          </GuestRoute>
        }
      />
      <Route
        path="/register"
        element={
          <GuestRoute>
            <RegisterPage />
          </GuestRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="properties" element={<PropertiesPage />} />
        <Route path="properties/new" element={<AddPropertyPage />} />
        <Route path="properties/:id" element={<PropertyDetailPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="rankings" element={<RankingsPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>

      <Route
        path="/admin"
        element={
          <ProtectedRoute roles={['admin']}>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="users" element={<AdminUsersPage />} />
        <Route path="settings" element={<AdminSettingsPage />} />
      </Route>
    </Routes>
  )
}
