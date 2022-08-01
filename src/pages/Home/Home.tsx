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

const WhatIsJMC = () => {
    return (
        <div className="flex-col flex">
            <p className="font-minecraft font-bold underline text-white text-[10vw] md:text-[5vh]">
                What is JMC
            </p>
            <img
                src={require("../../assets/image/code/what_is_jmc.png")}
                alt="Code Example"
                className="rounded-[2rem]"
            />
        </div>
    );
};

const DownwardArrow = () => {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 490.03 490.03"
            width="48"
            height="86"
            className="mx-auto fill-white animate-[bouncing-arrow_1s_infinite]"
        >
            <path
                d="M245.015,490.015L490.03,234.132l-69.802-69.773L490.03,91.46L398.548,0.015L245.015,160.352L91.482,0.015L0,91.46
	l69.802,72.899L0,234.132L245.015,490.015z M42.904,91.924l48.099-48.076l154.012,160.831L399.027,43.847l48.099,48.076
	L245.015,303.009L42.904,91.924z M91.003,186.52l154.012,160.846L399.027,186.52l48.099,48.076L245.015,445.674L42.904,234.596
	L91.003,186.52z"
            />
        </svg>
    );
};

const WhatIsJMCDesc = () => {
    return (
        <div className="flex-col flex">
            <div className="">
                <img
                    src={require("../../assets/image/minecraft_wallpaper.jpg")}
                    alt="Code Example"
                    className="max-w-[50vw] max-h-[30vh] aspect-square rounded-sm mx-auto"
                />
            </div>
            <div className="text-center font-minecraft text-white">
                <p>
                    JMC (JavaScript-like Minecraft Function) is a custom
                    language for making Minecraft Datapack.
                </p>
                <p>Write a JMC file</p>
                <DownwardArrow />
                <p>Run Compiler</p>
                <DownwardArrow />
                <p>Entire Minecraft Datapack</p>
            </div>
        </div>
    );
};

const Home = () => {
    return (
        <>
            <section className="h-screen w-screen main-section flex flex-row-reverse items-center flex-wrap justify-between overflow-y-hidden overflow-hidden pt-20 px-10 pb-10">
                <JMC_Icon />
                <Mantra />
            </section>
            <section className="h-screen bg-[#002029] flex flex-wrap overflow-y-hidden">
                <WhatIsJMC />
                <WhatIsJMCDesc />
            </section>
            <section className="h-screen bg-[#18001A]"></section>
        </>
    );
};

export default Home;
