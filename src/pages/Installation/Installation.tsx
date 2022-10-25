import React from "react";
import { Link } from "react-router-dom";

const Installation = () => {
    return (
        <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-secondary text-3xl md:text-6xl mx-auto">
                Installation
            </div>
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Download JMC
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;Download{" "}
                    <a
                        href="https://github.com/WingedSeal/jmc/releases/latest/download/JMC.exe"
                        className="underline"
                    >
                        JMC.exe
                    </a>{" "}
                    (Executable) from{" "}
                    <Link to="/download" className="underline">
                        download page
                    </Link>
                    .
                </p>
            </div>
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                File location
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;In "datapacks" folder of your world file (Usually{" "}
                    <code>.minecraft/saves/world_name/datapacks</code>). Create
                    a new datapack folder. And put JMC.exe in that folder.
                </p>
            </div>
            <img
                src={require("../../assets/image/installation/file_location.png")}
                alt="File Location Example"
                width="927"
                height="195"
                className="max-w-[90vw] minecraft mx-auto my-3"
            />
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Configuration
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    &emsp;Run JMC.exe and it'll greet you with configuration
                    settings. Select datapack's namespace, description and
                    pack_format. You can use default for{" "}
                    <code> Main JMC file</code> and{" "}
                    <code>Output directory</code>.
                </p>
            </div>
            <img
                src={require("../../assets/image/installation/config.png")}
                alt="File Location Example"
                width="1215"
                height="299"
                className="max-w-[90vw] minecraft mx-auto my-3"
            />
        </section>
    );
};
export default Installation;
