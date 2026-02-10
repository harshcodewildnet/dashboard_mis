import { Select } from "@mantine/core";
import { IconFilter } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { auth } from "../auth/auth";

export interface Department {
    department_key: string;
    department_name: string;
    cost_centre_parent: string;
}

interface DepartmentFilterProps {
    value: string | null;
    onChange: (value: string | null) => void;
}

export function DepartmentFilter({ value, onChange }: DepartmentFilterProps) {
    const [departments, setDepartments] = useState<Department[]>([]);
    const [loading, setLoading] = useState(false);
    const user = auth.getUser();

    useEffect(() => {
        // Only fetch if user is admin
        if (!user || user.role !== "ADMIN") {
            return;
        }

        const fetchDepartments = async () => {
            setLoading(true);
            try {
                const response = await api.get<Department[]>("/api/departments");
                setDepartments(response.data);
            } catch (error) {
                console.error("Failed to fetch departments:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDepartments();
    }, [user]);

    // Only show for admin users - AFTER hooks
    if (!user || user.role !== "ADMIN") {
        return null;
    }

    const options = [
        { value: "", label: "All Departments" },
        ...departments.map((dept) => ({
            value: dept.department_key,
            label: dept.department_name,
        })),
    ];

    return (
        <Select
            placeholder="Filter by department"
            data={options}
            value={value || ""}
            onChange={(val) => onChange(val === "" ? null : val)}
            leftSection={<IconFilter size={16} />}
            disabled={loading}
            clearable
            searchable
            w={250}
            size="sm"
        />
    );
}
