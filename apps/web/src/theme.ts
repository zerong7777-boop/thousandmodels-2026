import type { ThemeConfig } from "antd";

export const appTheme: ThemeConfig = {
  token: {
    colorPrimary: "#245b4f",
    colorInfo: "#2f6f9f",
    colorWarning: "#b7791f",
    colorError: "#b42318",
    borderRadius: 8,
    fontFamily: 'Inter, "Microsoft YaHei", Arial, sans-serif'
  },
  components: {
    Layout: {
      bodyBg: "#f4f6f5",
      siderBg: "#173d36",
      headerBg: "#ffffff"
    },
    Card: {
      borderRadiusLG: 8
    },
    Menu: {
      darkItemBg: "#173d36",
      darkSubMenuItemBg: "#173d36"
    }
  }
};
