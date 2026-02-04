import { AppShell, Burger, Group, NavLink, ScrollArea, Text, Button, Avatar, Menu } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconChartArea, IconHome, IconLogout, IconNotebook, IconShoppingBag, IconUser } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { LedgerPage } from "./pages/LedgerPage";
import { RowsPage } from "./pages/RowsPage";
import { SalesPage } from "./pages/SalesPage";
import { SummaryPage } from "./pages/SummaryPage";
import { LoginPage } from "./pages/LoginPage";
import { auth, User } from "./auth/auth";

const links = [
  { label: "Executive Summary", to: "/", icon: <IconHome size={16} /> },
  { label: "Sales", to: "/sales", icon: <IconShoppingBag size={16} /> },
  { label: "Ledger Explorer", to: "/ledger", icon: <IconChartArea size={16} /> },
  { label: "Raw Rows", to: "/rows", icon: <IconNotebook size={16} /> }
];

export default function App() {
  const [opened, { toggle, close }] = useDisclosure();
  const [user, setUser] = useState<User | null>(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      if (auth.isAuthenticated()) {
        try {
          const userData = await auth.fetchMe();
          setUser(userData);
        } catch (err) {
          auth.logout();
        }
      }
      setIsAuthChecking(false);
    };
    checkAuth();
  }, []);

  const current = useMemo(() => location.pathname, [location.pathname]);

  const handleLogout = () => {
    auth.logout();
    setUser(null);
    navigate('/');
  };

  if (isAuthChecking) return null;

  if (!user) {
    return <LoginPage onLoginSuccess={() => setUser(auth.getUser())} />;
  }

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 240, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Text fw={900} size="xl" variant="gradient" gradient={{ from: 'blue', to: 'cyan', deg: 90 }}>MIS</Text>
            <Text fw={700} hiddenFrom="xs">Dashboard</Text>
          </Group>

          <Group>
            <Box hiddenFrom="xs">
              <Text size="xs" fw={700} ta="right">{user.email}</Text>
              <Text size="xs" c="dimmed" ta="right">{user.role}: {user.cost_centre_parent || 'Global'}</Text>
            </Box>
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <Avatar color="blue" radius="xl" style={{ cursor: 'pointer' }}>
                  {user.email.charAt(0).toUpperCase()}
                </Avatar>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Label>Application</Menu.Label>
                <Menu.Item leftSection={<IconUser size={14} />}>Profile</Menu.Item>
                <Menu.Divider />
                <Menu.Item
                  color="red"
                  leftSection={<IconLogout size={14} />}
                  onClick={handleLogout}
                >
                  Logout
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <AppShell.Section grow component={ScrollArea}>
          {links.map((link) => (
            <NavLink
              key={link.to}
              label={link.label}
              leftSection={link.icon}
              active={current === link.to}
              onClick={() => {
                navigate(link.to);
                close();
              }}
              styles={{
                root: { borderRadius: 8, marginBottom: 4 }
              }}
            />
          ))}
        </AppShell.Section>
        <AppShell.Section>
          <Text size="xs" c="dimmed" ta="center" p="xs">v0.1.0-rbac</Text>
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<SummaryPage />} />
          <Route path="/sales" element={<SalesPage />} />
          <Route path="/ledger" element={<LedgerPage />} />
          <Route path="/rows" element={<RowsPage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  );
}

// Dummy Box for the header layout since I used it above
function Box({ children, ...props }: any) {
  return <div {...props}>{children}</div>
}
