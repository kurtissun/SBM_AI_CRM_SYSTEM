import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  User,
  Camera,
  Palette,
  Bell,
  Shield,
  Globe,
  Settings as SettingsIcon,
  Upload,
  Trash2,
  Eye,
  EyeOff,
  Smartphone,
  Mail,
  Lock,
  Key,
  Monitor,
  Sun,
  Moon,
  Download,
  AlertTriangle,
  Save,
  X,
  Check,
  Clock,
  DollarSign,
  Calendar,
  LogOut,
  Trash,
  RefreshCw,
} from "lucide-react";
import { useTranslation } from "@/contexts/TranslationContext";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuthStore } from "@/stores/authStore";
import { toast } from "react-hot-toast";
import axios from "axios";

interface SettingsTabProps {
  id: string;
  label: string;
  icon: React.ElementType;
  content: React.ReactNode;
}

export const Settings: React.FC = () => {
  const { t } = useTranslation();
  const { theme, customBackground, applyBackground, setTheme } = useTheme();
  const { user, updateUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState("profile");
  const [profileData, setProfileData] = useState({
    username: user?.username || "",
    email: user?.email || "",
    fullName: user?.fullName || "",
    jobTitle: user?.jobTitle || "",
    company: user?.company || "",
    phone: user?.phone || "",
    bio: user?.bio || "",
    profilePicture: user?.profilePicture || null,
  });
  const [backgroundTheme, setBackgroundTheme] = useState(theme);
  const [isLoading, setIsLoading] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    marketing: true,
    security: true,
    updates: false,
  });
  const [privacy, setPrivacy] = useState({
    twoFactorEnabled: false,
    showPassword: false,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const backgroundInputRef = useRef<HTMLInputElement>(null);

  // Load user profile on component mount
  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const response = await axios.get("/api/user/profile");
      const profile = response.data;
      setUserProfile(profile);
      setProfileData({
        username: profile.username || user?.username || "",
        email: profile.email || user?.email || "",
        fullName: profile.display_name || user?.fullName || "",
        jobTitle: user?.jobTitle || "",
        company: user?.company || "",
        phone: user?.phone || "",
        bio: user?.bio || "",
        profilePicture: profile.profile_picture || user?.profilePicture || null,
      });
      setBackgroundTheme(profile.theme || "dark");
      applyBackground(profile.custom_background);
    } catch (error) {
      console.error("Failed to load user profile:", error);
      // Use existing user data as fallback
    }
  };

  const handleProfileUpdate = async () => {
    setIsLoading(true);
    try {
      const updateData = {
        display_name: profileData.fullName,
        email: profileData.email,
        theme: backgroundTheme,
        custom_background: customBackground,
        profile_picture: profileData.profilePicture,
      };

      const response = await axios.put("/api/user/profile", updateData);

      // Update auth store with new data
      updateUser({
        ...user,
        fullName: profileData.fullName,
        email: profileData.email,
        profilePicture: profileData.profilePicture,
      });

      toast.success(t("settings.saved"));
    } catch (error) {
      console.error("Failed to update profile:", error);
      toast.error("Failed to save settings");
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfilePictureUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsLoading(true);
      try {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const result = e.target?.result as string;
          setProfileData((prev) => ({ ...prev, profilePicture: result }));

          // Save to backend immediately
          await axios.put("/api/user/profile", {
            profile_picture: result,
          });

          // Update auth store
          updateUser({ ...user, profilePicture: result });

          toast.success(t("settings.saved"));
          setIsLoading(false);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error("Failed to upload profile picture:", error);
        toast.error("Failed to upload profile picture");
        setIsLoading(false);
      }
    }
  };

  const handleBackgroundUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsLoading(true);
      try {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const result = e.target?.result as string;
          applyBackground(result);

          // Save to backend immediately
          await axios.put("/api/user/profile", {
            custom_background: result,
          });

          toast.success(t("settings.saved"));
          setIsLoading(false);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error("Failed to upload background:", error);
        toast.error("Failed to upload background");
        setIsLoading(false);
      }
    }
  };

  const removeProfilePicture = async () => {
    setIsLoading(true);
    try {
      await axios.delete("/api/user/profile-picture");
      setProfileData((prev) => ({ ...prev, profilePicture: null }));
      updateUser({ ...user, profilePicture: null });
      toast.success(t("settings.saved"));
    } catch (error) {
      console.error("Failed to remove profile picture:", error);
      toast.error("Failed to remove profile picture");
    } finally {
      setIsLoading(false);
    }
  };

  const defaultBackgrounds = [
    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
  ];

  const tabs: SettingsTabProps[] = [
    {
      id: "profile",
      label: t("settings.profile"),
      icon: User,
      content: (
        <div className="space-y-6">
          {/* Profile Picture Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.profilePicture")}
            </h3>
            <div className="flex items-center space-x-6">
              <div className="relative">
                {profileData.profilePicture ? (
                  <img
                    src={profileData.profilePicture}
                    alt="Profile"
                    className="w-20 h-20 rounded-full object-cover border-4 border-white shadow-lg"
                  />
                ) : (
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <User className="w-10 h-10 text-white" />
                  </div>
                )}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="absolute -bottom-2 -right-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors"
                >
                  <Camera className="w-4 h-4" />
                </button>
              </div>
              <div className="flex-1">
                <div className="flex space-x-3">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                  >
                    <Upload className="w-4 h-4" />
                    <span>{t("settings.uploadPhoto")}</span>
                  </button>
                  {profileData.profilePicture && (
                    <button
                      onClick={removeProfilePicture}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>{t("settings.removePhoto")}</span>
                    </button>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Upload a profile picture to personalize your account
                </p>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleProfilePictureUpload}
              className="hidden"
            />
          </div>

          {/* Personal Information */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.personalInfo")}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.username")}
                </label>
                <input
                  type="text"
                  value={profileData.username}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      username: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.email")}
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      email: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.fullName")}
                </label>
                <input
                  type="text"
                  value={profileData.fullName}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      fullName: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.jobTitle")}
                </label>
                <input
                  type="text"
                  value={profileData.jobTitle}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      jobTitle: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.company")}
                </label>
                <input
                  type="text"
                  value={profileData.company}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      company: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.phone")}
                </label>
                <input
                  type="tel"
                  value={profileData.phone}
                  onChange={(e) =>
                    setProfileData((prev) => ({
                      ...prev,
                      phone: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.bio")}
                </label>
                <textarea
                  value={profileData.bio}
                  onChange={(e) =>
                    setProfileData((prev) => ({ ...prev, bio: e.target.value }))
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tell us about yourself..."
                />
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button
                onClick={handleProfileUpdate}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{isLoading ? "Saving..." : t("settings.save")}</span>
              </button>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "appearance",
      label: t("settings.appearance"),
      icon: Palette,
      content: (
        <div className="space-y-6">
          {/* Color Scheme */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.colorScheme")}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {[
                { id: "light", label: t("settings.lightMode"), icon: Sun },
                { id: "dark", label: t("settings.darkMode"), icon: Moon },
                { id: "auto", label: t("settings.autoMode"), icon: Monitor },
                { id: "pure-black", label: "Pure Black", icon: Moon },
                { id: "pure-white", label: "Pure White", icon: Sun },
              ].map((theme) => (
                <button
                  key={theme.id}
                  onClick={async () => {
                    setBackgroundTheme(
                      theme.id as
                        | "light"
                        | "dark"
                        | "auto"
                        | "pure-black"
                        | "pure-white"
                    );
                    setTheme(
                      theme.id as
                        | "light"
                        | "dark"
                        | "auto"
                        | "pure-black"
                        | "pure-white"
                    );
                    try {
                      await axios.put("/api/user/profile", { theme: theme.id });
                      toast.success("Theme updated");
                    } catch (error) {
                      console.error("Failed to update theme:", error);
                      toast.error("Failed to update theme");
                    }
                  }}
                  className={`p-4 border-2 rounded-lg flex flex-col items-center space-y-2 transition-colors ${
                    backgroundTheme === theme.id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <theme.icon className="w-8 h-8 text-gray-600" />
                  <span className="font-medium">{theme.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Background */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.customBackground")}
            </h3>

            {/* Default Backgrounds */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                {t("settings.defaultBackgrounds")}
              </h4>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {defaultBackgrounds.map((bg, index) => (
                  <button
                    key={index}
                    onClick={async () => {
                      applyBackground(bg);
                      try {
                        await axios.put("/api/user/profile", {
                          custom_background: bg,
                        });
                        toast.success("Background updated");
                      } catch (error) {
                        console.error("Failed to update background:", error);
                        toast.error("Failed to update background");
                      }
                    }}
                    className={`w-full h-16 rounded-lg border-2 transition-colors ${
                      customBackground === bg
                        ? "border-blue-500"
                        : "border-gray-200"
                    }`}
                    style={{ background: bg }}
                  />
                ))}
              </div>
            </div>

            {/* Upload Custom Background */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                {t("settings.uploadBackground")}
              </h4>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => backgroundInputRef.current?.click()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>{t("settings.uploadBackground")}</span>
                </button>
                {customBackground &&
                  !defaultBackgrounds.includes(customBackground) && (
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-12 h-12 rounded-lg border border-gray-200"
                        style={{
                          backgroundImage: `url(${customBackground})`,
                          backgroundSize: "cover",
                        }}
                      />
                      <button
                        onClick={async () => {
                          applyBackground(null);
                          try {
                            await axios.delete("/api/user/background");
                            toast.success("Background removed");
                          } catch (error) {
                            console.error(
                              "Failed to remove background:",
                              error
                            );
                            toast.error("Failed to remove background");
                          }
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  )}
              </div>
              <input
                ref={backgroundInputRef}
                type="file"
                accept="image/*"
                onChange={handleBackgroundUpload}
                className="hidden"
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "notifications",
      label: t("settings.notifications"),
      icon: Bell,
      content: (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.notifications")}
            </h3>
            <div className="space-y-4">
              {[
                {
                  key: "email",
                  label: t("settings.emailNotifications"),
                  icon: Mail,
                },
                {
                  key: "push",
                  label: t("settings.pushNotifications"),
                  icon: Bell,
                },
                {
                  key: "sms",
                  label: t("settings.smsNotifications"),
                  icon: Smartphone,
                },
                {
                  key: "marketing",
                  label: t("settings.marketingEmails"),
                  icon: Mail,
                },
                {
                  key: "security",
                  label: t("settings.securityAlerts"),
                  icon: Shield,
                },
                {
                  key: "updates",
                  label: t("settings.systemUpdates"),
                  icon: RefreshCw,
                },
              ].map((item) => (
                <div
                  key={item.key}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <item.icon className="w-5 h-5 text-gray-600" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  <button
                    onClick={() =>
                      setNotifications((prev) => ({
                        ...prev,
                        [item.key]: !prev[item.key as keyof typeof prev],
                      }))
                    }
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      notifications[item.key as keyof typeof notifications]
                        ? "bg-blue-600"
                        : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        notifications[item.key as keyof typeof notifications]
                          ? "translate-x-5"
                          : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "privacy",
      label: t("settings.privacy"),
      icon: Shield,
      content: (
        <div className="space-y-6">
          {/* Password Change */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.changePassword")}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.currentPassword")}
                </label>
                <div className="relative">
                  <input
                    type={privacy.showPassword ? "text" : "password"}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() =>
                      setPrivacy((prev) => ({
                        ...prev,
                        showPassword: !prev.showPassword,
                      }))
                    }
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {privacy.showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.newPassword")}
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t("settings.confirmPassword")}
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                {t("settings.changePassword")}
              </button>
            </div>
          </div>

          {/* Two-Factor Authentication */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t("settings.twoFactorAuth")}
            </h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-gray-600">
                  Add an extra layer of security to your account
                </p>
              </div>
              <button
                onClick={() =>
                  setPrivacy((prev) => ({
                    ...prev,
                    twoFactorEnabled: !prev.twoFactorEnabled,
                  }))
                }
                className={`px-4 py-2 rounded-lg transition-colors ${
                  privacy.twoFactorEnabled
                    ? "bg-red-600 text-white hover:bg-red-700"
                    : "bg-green-600 text-white hover:bg-green-700"
                }`}
              >
                {privacy.twoFactorEnabled
                  ? t("settings.disable2FA")
                  : t("settings.enable2FA")}
              </button>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {t("settings.title")}
        </h1>
        <p className="text-gray-600 mt-2">{t("settings.subtitle")}</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:w-64">
          <nav className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? "bg-blue-600 text-white"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content Area */}
        <div className="flex-1">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {tabs.find((tab) => tab.id === activeTab)?.content}
          </motion.div>
        </div>
      </div>
    </div>
  );
};
