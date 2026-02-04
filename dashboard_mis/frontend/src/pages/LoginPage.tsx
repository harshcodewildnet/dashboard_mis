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
    Box
} from '@mantine/core';
import { IconAlertCircle, IconLock } from '@tabler/icons-react';
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
        <Container size={420} my={80}>
            <Title order={1} ta="center" fw={900}>
                MIS Dashboard
            </Title>
            <Text c="dimmed" size="sm" ta="center" mt={5}>
                Sign in to access your department reports
            </Text>

            <Paper withBorder shadow="md" p={30} mt={30} radius="md">
                <form onSubmit={handleSubmit}>
                    {error && (
                        <Alert icon={<IconAlertCircle size="1rem" />} title="Login Failed" color="red" mb="md">
                            {error}
                        </Alert>
                    )}

                    <TextInput
                        label="Email Address"
                        placeholder="admin@company.com"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.currentTarget.value)}
                    />
                    <PasswordInput
                        label="Password"
                        placeholder="Your password"
                        required
                        mt="md"
                        value={password}
                        onChange={(e) => setPassword(e.currentTarget.value)}
                    />

                    <Button fullWidth mt="xl" type="submit" loading={loading} leftSection={<IconLock size={16} />}>
                        Sign in
                    </Button>
                </form>
            </Paper>

            <Center mt="xl">
                <Box ta="center">
                    <Text size="xs" c="dimmed">Test Credentials:</Text>
                    <Text size="xs" c="dimmed">admin@company.com / admin123</Text>
                    <Text size="xs" c="dimmed">dm@company.com / dm123</Text>
                </Box>
            </Center>
        </Container>
    );
}
