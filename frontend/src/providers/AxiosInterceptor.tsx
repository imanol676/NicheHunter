"use client";

import { useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { apiClient } from "@/lib/apiClient";

export function AxiosInterceptor({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();

  useEffect(() => {
    const requestInterceptor = apiClient.interceptors.request.use(
      async (config) => {
        const token = await getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      apiClient.interceptors.request.eject(requestInterceptor);
    };
  }, [getToken]);

  return <>{children}</>;
}
