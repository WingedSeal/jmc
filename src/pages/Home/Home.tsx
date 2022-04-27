import React from "react";
import "./Home.css";

const Home = () => {
    return (
        <>
            <section className="h-screen main-section flex flex-row-reverse items-center flex-wrap justify-between overflow-y-hidden">
                <img
                    src={require("../../assets/image/jmc_icon.png")}
                    alt="JMC-icon"
                    className="h-[30vh] aspect-square mx-auto md:h-1/4 p-5 mt-14"
                />
                <div className="font-minecraft-ten text-white h-1/4 flex flex-col justify-center text-center md:text-right mx-auto text-[9vw] md:text-[6vh] p-5 md:mt-14">
                    <p className="whitespace-nowrap">JavaScript-like</p>
                    <p>Minecraft</p>
                    <p>Function</p>
                </div>
                <div className="flex flex-nowrap flex-col w-1/10 p-5 mx-auto mb-5">
                    <span className="text-[#97F544] text-6xl md:text-9xl flex flex-nowrap flex-row-reverse">
                        <img
                            src={require("../../assets/image/minecraft/sugar_cane.png")}
                            alt="minecraft:sugarcane"
                            className="aspect-square h-[1em] minecraft mx-3"
                        />
                        Simple
                    </span>
                    <span className="text-[#F3C12A] text-6xl md:text-9xl flex flex-nowrap flex-row-reverse">
                        Quick
                        <img
                            src={require("../../assets/image/minecraft/powered_rail_on.png")}
                            alt="minecraft:powered_rail"
                            className="aspect-square h-[1em] minecraft mx-3"
                        />
                    </span>
                    <span className="text-[#B7B7B7] text-5xl md:text-8xl flex flex-nowrap flex-row-reverse">
                        <img
                            src={require("../../assets/image/minecraft/enchanted_book.png")}
                            alt="minecraft:enchanted_book"
                            className="aspect-square h-[1em] minecraft mx-3"
                        />
                        Organized
                    </span>
                </div>
            </section>
            <section className="h-screen bg-[#002029]"></section>
            <section className="h-screen bg-[#18001A]"></section>
        </>
    );
};

export default Home;
