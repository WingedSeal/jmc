import React from "react";
import "./Home.css";

const Mantra = () => {
    return (
        <div className="flex flex-nowrap flex-col mx-auto ">
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
    );
};

const JMC_Icon = () => {
    return (
        <div className="flex flex-wrap flex-row-reverse h-1/16 mx-auto">
            <img
                src={require("../../assets/image/jmc_icon.png")}
                alt="JMC-icon"
                className="max-w-[50vw] max-h-[25vh] aspect-square mx-auto"
            />
            <div className="font-minecraft-ten text-white h-full flex flex-col justify-center text-center md:text-right mx-auto text-[10vw] md:text-[5vh] pr-5">
                <p className="whitespace-nowrap">JavaScript-like</p>
                <p>Minecraft</p>
                <p>Function</p>
            </div>
        </div>
    );
};

const Home = () => {
    return (
        <>
            <section className="h-screen main-section flex flex-row-reverse items-center flex-wrap justify-between overflow-y-hidden pt-20 px-10 pb-10">
                <JMC_Icon />
                <Mantra />
            </section>
            <section className="h-screen bg-[#002029]"></section>
            <section className="h-screen bg-[#18001A]"></section>
        </>
    );
};

export default Home;
