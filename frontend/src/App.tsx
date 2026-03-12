import { AppShell, Burger, Group, NavLink, ScrollArea, Text, Button, Stack, ActionIcon, Divider, rem, Tooltip } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconChartArea, IconCoin, IconHome, IconNotebook, IconReceipt, IconShoppingBag, IconLogout, IconLayoutDashboard } from "@tabler/icons-react";
import { useMemo, useState, useEffect } from "react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { ExpensePage } from "./pages/ExpensePage";
import { HomePage } from "./pages/HomePage";
import { IncomePage } from "./pages/IncomePage";
import { LedgerPage } from "./pages/LedgerPage";
import { RowsPage } from "./pages/RowsPage";
import { SalesPage } from "./pages/SalesPage";
import { SummaryPage } from "./pages/SummaryPage";
import { LoginPage } from "./pages/LoginPage";
import { auth } from "./auth/auth";
import { DepartmentFilter } from "./components/DepartmentFilter";

const links = [
  { label: "Overview", to: "/", icon: <IconLayoutDashboard size={18} stroke={1.5} /> },
  { label: "Revenue", to: "/income", icon: <IconCoin size={18} stroke={1.5} /> },
  { label: "Expenses", to: "/expense", icon: <IconReceipt size={18} stroke={1.5} /> },
  { label: "Sales Analysis", to: "/sales", icon: <IconShoppingBag size={18} stroke={1.5} /> },
  { label: "Ledger Explorer", to: "/ledger", icon: <IconChartArea size={18} stroke={1.5} /> },
  { label: "Executive Summary", to: "/summary", icon: <IconHome size={18} stroke={1.5} /> },
  { label: "Transaction Logs", to: "/rows", icon: <IconNotebook size={18} stroke={1.5} /> }
];

export default function App() {
  const [opened, { toggle, close }] = useDisclosure();
  const [authenticated, setAuthenticated] = useState(auth.isAuthenticated());
  const [selectedDepartment, setSelectedDepartment] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  const current = useMemo(() => location.pathname, [location.pathname]);

  useEffect(() => {
    if (authenticated) {
      auth.fetchMe().catch(() => {
        setAuthenticated(false);
      });
    }
  }, [authenticated]);

  const handleLoginSuccess = () => {
    setAuthenticated(true);
    navigate("/");
  };

  const handleLogout = () => {
    auth.logout();
    setAuthenticated(false);
    navigate("/");
  };

  if (!authenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <AppShell
      header={{ height: 56 }}
      navbar={{ width: 240, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header style={{ borderBottom: '1px solid var(--mantine-color-slate-2)', backdropFilter: 'blur(8px)', backgroundColor: 'rgba(255, 255, 255, 0.8)' }}>
        <Group h="100%" px="xl" justify="space-between">
          <Group gap="xl">
            <Group gap="md">
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
              <IconLayoutDashboard size={28} color="var(--mantine-color-indigo-6)" stroke={1.5} />
              <Text fw={900} size="xl" style={{ letterSpacing: '-1px' }}>
                MIS <Text span c="indigo.6">CORE</Text>
              </Text>
            </Group>
            
            <Group gap="xs" visibleFrom="md" style={{ 
              backgroundColor: 'var(--mantine-color-slate-0)', 
              padding: '6px 12px', 
              borderRadius: '8px',
              border: '1px solid var(--mantine-color-slate-2)',
              cursor: 'pointer'
            }}>
              <IconNotebook size={14} color="var(--mantine-color-slate-5)" />
              <Text size="xs" c="dimmed" fw={600}>Press ⌘K to search...</Text>
            </Group>
          </Group>

          <Group gap="lg">
            <DepartmentFilter value={selectedDepartment} onChange={setSelectedDepartment} />
            
            <Divider orientation="vertical" />
            
            <Group gap="xs">
              <Stack gap={0} align="flex-end" visibleFrom="sm">
                <Text size="xs" fw={700} c="slate.9" style={{ lineHeight: 1 }}>{auth.getUser()?.email?.split('@')[0]}</Text>
                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase', fontSize: rem(9) }}>System {auth.getUser()?.role}</Text>
              </Stack>
              <Tooltip label="Secure Logout" position="bottom" withArrow>
                <ActionIcon 
                  variant="light" 
                  color="red" 
                  size="lg" 
                  radius="md" 
                  onClick={handleLogout}
                >
                  <IconLogout size={18} stroke={1.5} />
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md" style={{ borderRight: '1px solid var(--mantine-color-slate-2)', backgroundColor: 'var(--mantine-color-slate-0)' }}>
        <AppShell.Section grow component={ScrollArea} mx="-md" px="md">
          <Stack gap={4}>
            {links.map((link) => (
              <NavLink
                key={link.to}
                label={link.label}
                leftSection={link.icon}
                active={current === link.to}
                variant="filled"
                styles={{
                  root: {
                    borderRadius: 'var(--mantine-radius-md)',
                    transition: 'all 200ms ease',
                    fontWeight: current === link.to ? 600 : 500,
                  },
                  label: {
                    fontSize: 'var(--mantine-font-size-sm)',
                  }
                }}
                onClick={() => {
                  navigate(link.to);
                  close();
                }}
              />
            ))}
          </Stack>
        </AppShell.Section>
        
        <AppShell.Section pt="md" style={{ borderTop: '1px solid var(--mantine-color-slate-2)' }}>
          <Group justify="center" p="xs">
            <Text size="xs" c="dimmed" fw={500}>v2.0.0 Stable</Text>
          </Group>
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<HomePage departmentKey={selectedDepartment} />} />
          <Route path="/income" element={<IncomePage departmentKey={selectedDepartment} />} />
          <Route path="/expense" element={<ExpensePage departmentKey={selectedDepartment} />} />
          <Route path="/sales" element={<SalesPage departmentKey={selectedDepartment} />} />
          <Route path="/ledger" element={<LedgerPage departmentKey={selectedDepartment} />} />
          <Route path="/rows" element={<RowsPage departmentKey={selectedDepartment} />} />
          <Route path="/summary" element={<SummaryPage departmentKey={selectedDepartment} />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  );
}
