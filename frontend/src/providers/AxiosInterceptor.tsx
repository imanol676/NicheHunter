"use client";

import { useLayoutEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { apiClient } from "@/lib/apiClient";

export function AxiosInterceptor({ children }: { children: React.ReactNode }) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  useLayoutEffect(() => {
    const requestInterceptor = apiClient.interceptors.request.use(
      async (config) => {
        if (isLoaded && isSignedIn) {
          const token = await getToken();
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      apiClient.interceptors.request.eject(requestInterceptor);
    };
  }, [getToken, isLoaded, isSignedIn]);

  return <>{children}</>;
}
