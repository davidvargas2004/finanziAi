import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";



const firebaseConfig = {
    apiKey: "AIzaSyAeu-n-gQkDfohP0c-DflNFTgFMpqRBFtM",
    authDomain: "finanziai.firebaseapp.com",
    projectId: "finanziai",
    storageBucket: "finanziai.firebasestorage.app",
    messagingSenderId: "782295902622",
    appId: "1:782295902622:web:0cc85c7300c0f9cb3dce8f",
    measurementId: "G-YK37J0EVD4"
  };



// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);



export {analytics};

