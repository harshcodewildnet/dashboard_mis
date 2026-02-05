import { AppShell, Burger, Group, NavLink, ScrollArea, Text, Button } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import {
  IconChartArea,
  IconCoin,
  IconHome,
  IconNotebook,
  IconReceipt,
  IconShoppingBag,
  IconLogout
} from "@tabler/icons-react";
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

const links = [
  { label: "Home", to: "/", icon: <IconHome size={16} /> },
  { label: "Income Details", to: "/income", icon: <IconCoin size={16} /> },
  { label: "Expense Details", to: "/expense", icon: <IconReceipt size={16} /> },
  { label: "Sales", to: "/sales", icon: <IconShoppingBag size={16} /> },
  { label: "Ledger Explorer", to: "/ledger", icon: <IconChartArea size={16} /> },
  { label: "Raw Rows", to: "/rows", icon: <IconNotebook size={16} /> }
];

export default function App() {
  const [opened, { toggle, close }] = useDisclosure();
  const [authenticated, setAuthenticated] = useState(auth.isAuthenticated());
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
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Text fw={700}>MIS Dashboard</Text>
          </Group>
          <Group gap="sm">
            <Text size="sm" c="dimmed">
              {auth.getUser()?.email}
            </Text>
            <Button
              variant="subtle"
              color="gray"
              size="compact-xs"
              onClick={handleLogout}
              leftSection={<IconLogout size={14} />}
            >
              Logout
            </Button>
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
            />
          ))}
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/income" element={<IncomePage />} />
          <Route path="/expense" element={<ExpensePage />} />
          <Route path="/sales" element={<SalesPage />} />
          <Route path="/ledger" element={<LedgerPage />} />
          <Route path="/rows" element={<RowsPage />} />
          <Route path="/summary" element={<SummaryPage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  );
}
