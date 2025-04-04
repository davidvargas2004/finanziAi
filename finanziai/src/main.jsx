import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes,Route } from 'react-router-dom';
import './index.css'
import App from './App.jsx'
import Registro from './Registro.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
      <BrowserRouter>
        <Routes>
            <Route path="/indexApp" element={<App/>}/>
            <Route path="/registro" element={<Registro/>}/>
        </Routes>
      </BrowserRouter>
  </StrictMode>,
)
