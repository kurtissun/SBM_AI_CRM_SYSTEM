import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";
import { toast } from "react-hot-toast";

interface User {
  id: string;
  email: string;
  username: string;
  name: string;
  role: string;
  permissions: string[];
  refreshKey?: string;
  refreshKeyExpiry?: string;
  fullName?: string;
  jobTitle?: string;
  company?: string;
  phone?: string;
  bio?: string;
  profilePicture?: string | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshKey: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  login: (emailOrUsername: string, password: string) => Promise<void>;
  createAccount: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  generateRefreshKey: () => Promise<string>;
  logout: () => void;
  checkAuth: () => void;
  updateToken: (token: string) => void;
  updateUser: (userData: Partial<User>) => void;
}

// Configure axios defaults
axios.defaults.baseURL = "/";
axios.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => {
    // Check for token refresh in headers
    const newToken = response.headers["x-new-access-token"];
    if (newToken) {
      useAuthStore.getState().updateToken(newToken);
    }
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      toast.error("Session expired. Please login again.");
    }
    return Promise.reject(error);
  }
);

// Helper function to generate 8-character refresh key
const generateRefreshKey = (): string => {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let result = "";
  for (let i = 0; i < 8; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// Helper function to get next week's date
const getNextWeekDate = (): string => {
  const nextWeek = new Date();
  nextWeek.setDate(nextWeek.getDate() + 7);
  return nextWeek.toISOString();
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshKey: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,

      login: async (emailOrUsername: string, password: string) => {
        set({ isLoading: true });
        try {
          // Determine if input is email or username
          const isEmail = emailOrUsername.includes("@");
          const loginData = {
            username: isEmail ? emailOrUsername.split("@")[0] : emailOrUsername,
            password,
          };

          const response = await axios.post("/auth/login", loginData);
          const { user_info, access_token } = response.data;

          // Create user object with proper format
          const user: User = {
            id: user_info.username,
            email: user_info.email,
            username: user_info.username,
            name: user_info.username,
            role: user_info.roles?.[0] || "user",
            permissions: user_info.permissions || [],
            refreshKey: get()?.refreshKey || "",
            refreshKeyExpiry: get().user?.refreshKeyExpiry,
          };

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            isInitialized: true,
          });

          toast.success(`Welcome back, ${user.username}!`);
        } catch (error: any) {
          set({ isLoading: false });
          const errorMsg = error.response?.data?.detail || "Login failed";
          toast.error(errorMsg);
          throw error;
        }
      },

      createAccount: async (
        username: string,
        email: string,
        password: string
      ) => {
        set({ isLoading: true });
        try {
          // For demo purposes, we'll create a simulated account
          if (username === "admin" && password === "admin123") {
            const newRefreshKey = generateRefreshKey();
            const refreshKeyExpiry = getNextWeekDate();

            const user: User = {
              id: username,
              email: email || `${username}@sbm.com`,
              username,
              name: username,
              role: "admin",
              permissions: [
                "read",
                "write",
                "admin",
                "manage_users",
                "manage_campaigns",
              ],
              refreshKey: newRefreshKey,
              refreshKeyExpiry,
            };

            set({
              user,
              refreshKey: newRefreshKey,
              token: "demo_token_" + Date.now(),
              isAuthenticated: true,
              isLoading: false,
              isInitialized: true,
            });

            toast.success("Account created successfully!");
            return;
          }

          throw new Error("Account creation only allowed for admin user");
        } catch (error: any) {
          set({ isLoading: false });
          toast.error(error.message || "Account creation failed");
          throw error;
        }
      },

      generateRefreshKey: async () => {
        try {
          const state = get();
          if (!state.user || state.user.role !== "admin") {
            throw new Error("Only admin users can generate refresh keys");
          }

          const newRefreshKey = generateRefreshKey();
          const refreshKeyExpiry = getNextWeekDate();

          set({
            refreshKey: newRefreshKey,
            user: {
              ...state.user,
              refreshKey: newRefreshKey,
              refreshKeyExpiry,
            },
          });

          toast.success("New refresh key generated!");
          return newRefreshKey;
        } catch (error: any) {
          toast.error(error.message || "Failed to generate refresh key");
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshKey: null,
          isAuthenticated: false,
          isInitialized: true,
        });
        window.location.href = "/login";
      },

      checkAuth: () => {
        const state = get();

        // If we have a token and user, mark as authenticated
        if (state.token && state.user) {
          set({ isAuthenticated: true, isInitialized: true });
        } else {
          set({ isAuthenticated: false, isInitialized: true });
        }
      },

      updateToken: (token: string) => {
        set({ token });
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          const updatedUser = { ...currentUser, ...userData };
          set({ user: updatedUser });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        refreshKey: state.refreshKey,
      }),
    }
  )
);
