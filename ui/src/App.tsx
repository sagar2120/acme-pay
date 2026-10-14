import { App as AntApp, ConfigProvider } from "antd";
import { NavLink, Route, Routes } from "react-router-dom";
import { AskChat } from "./components/AskChat";
import { PayAnswers } from "./pages/PayAnswers";
import { People } from "./pages/People";

const theme = {
  token: {
    colorPrimary: "#2F5D50",
    colorLink: "#2F5D50",
    colorText: "#1F2A2E",
    colorTextSecondary: "#5E6B67",
    colorBorderSecondary: "#E3E8E5",
    colorBgLayout: "#F5F7F6",
    borderRadius: 4,
    fontFamily: "'Public Sans', system-ui, sans-serif",
  },
};

export function App() {
  return (
    <ConfigProvider theme={theme}>
      <AntApp>
        <header className="masthead">
          <span className="product">ACME Pay</span>
          <nav aria-label="Main">
            <NavLink to="/" end>
              Pay answers
            </NavLink>
            <NavLink to="/people">People</NavLink>
          </nav>
        </header>
        <main className="page">
          <Routes>
            <Route path="/" element={<PayAnswers />} />
            <Route path="/people" element={<People />} />
          </Routes>
        </main>
        <AskChat />
      </AntApp>
    </ConfigProvider>
  );
}
