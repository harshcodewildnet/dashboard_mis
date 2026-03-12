import { useState } from 'react';
import {
    TextInput,
    PasswordInput,
    Paper,
    Title,
    Text,
    Container,
    Button,
    Alert,
    Center,
    Box,
    rem,
    Stack,
    Group
} from '@mantine/core';
import { IconAlertCircle, IconLock, IconUser, IconLayoutDashboard } from '@tabler/icons-react';
import { auth } from '../auth/auth';

interface LoginPageProps {
    onLoginSuccess: () => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await auth.login(email, password);
            onLoginSuccess();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid email or password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            style={{
                minHeight: '100vh',
                background: 'linear-gradient(135deg, var(--mantine-color-slate-0) 0%, var(--mantine-color-indigo-1) 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: rem(20)
            }}
        >
            <Container size={420} w="100%">
                <Stack align="center" gap="xl" mb={rem(40)}>
                    <Group gap="md">
                        <IconLayoutDashboard size={40} color="var(--mantine-color-indigo-6)" />
                        <Title order={1} fw={900} size={rem(32)} style={{ letterSpacing: '-1px' }}>
                            MIS <Text span c="indigo.6">CORE</Text>
                        </Title>
                    </Group>
                    <Box ta="center">
                        <Title order={2} size="h3" fw={700}>Welcome Back</Title>
                        <Text c="dimmed" size="sm" mt={5}>
                            Sign in to access your enterprise analytics suite
                        </Text>
                    </Box>
                </Stack>

                <Paper withBorder shadow="xl" p={40} radius="lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', backdropFilter: 'blur(10px)' }}>
                    <form onSubmit={handleSubmit}>
                        {error && (
                            <Alert icon={<IconAlertCircle size="1.2rem" />} title="Invalid Credentials" color="red" mb="lg" radius="md" variant="light">
                                {error}
                            </Alert>
                        )}

                        <TextInput
                            label="Corporate Email"
                            placeholder="name@company.com"
                            required
                            size="md"
                            leftSection={<IconUser size={18} stroke={1.5} />}
                            value={email}
                            onChange={(e) => setEmail(e.currentTarget.value)}
                        />
                        <PasswordInput
                            label="Safe Password"
                            placeholder="••••••••"
                            required
                            size="md"
                            mt="lg"
                            leftSection={<IconLock size={18} stroke={1.5} />}
                            value={password}
                            onChange={(e) => setPassword(e.currentTarget.value)}
                        />

                        <Button 
                            fullWidth 
                            mt={40} 
                            size="md" 
                            type="submit" 
                            loading={loading}
                            radius="md"
                            style={{ 
                                boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)',
                                transition: 'transform 150ms ease'
                            }}
                        >
                            Authorize Access
                        </Button>
                    </form>
                </Paper>

                <Stack mt="xl" gap="xs">
                    <Center>
                        <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Development Sandbox</Text>
                    </Center>
                    <Paper withBorder p="xs" radius="md" bg="slate.0">
                        <Stack gap={4}>
                            <Text size="xs" ta="center" fw={500}>admin@company.com / admin123</Text>
                            <Text size="xs" ta="center" fw={500}>dm@company.com / dm123</Text>
                        </Stack>
                    </Paper>
                </Stack>
            </Container>
        </Box>
    );
}
