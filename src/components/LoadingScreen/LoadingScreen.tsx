import React from "react";
import "./LoadingScreen.css";

const LoadingCircle = () => {
    return (
        <div
            id="wrapper"
            className="scale-[1.2] md:scale-[2.1] m-auto absolute"
        >
            <div className="profile-main-loader">
                <div className="loader">
                    <svg className="circular-loader" viewBox="25 25 50 50">
                        <circle
                            className="loader-path"
                            cx="50"
                            cy="50"
                            r="20"
                            fill="none"
                            stroke="#FFAA00"
                            strokeWidth="2"
                        />
                    </svg>
                </div>
            </div>
        </div>
    );
};

interface LoadingScreenInterface {
    isLoaded: boolean;
}

const LoadingScreen: React.FC<LoadingScreenInterface> = ({ isLoaded }) => {
    return (
        <div
            className={
                "transition-opacity duration-300 " +
                (isLoaded ? "opacity-0" : "opacity-100")
            }
        >
            <div className="w-screen h-screen fixed bg-gray-900 z-30 flex loading-screen">
                <LoadingCircle />
                <img
                    className="aspect-square max-w-[25vw] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-75 rounded-lg"
                    src={require("../../assets/image/jmc_icon192.png")}
                    alt="JMC-icon"
                />
            </div>
        </div>
    );
};

export default LoadingScreen;
