import React, { type ReactNode } from "react"; 
import Sidebar from "./Sidebar"; 

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="app-container">
      <Sidebar /> 
      {/* Nội dung chính */}
      <main className="main-content-area">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;