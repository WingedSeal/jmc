import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import LoadingScreen from "../../components/LoadingScreen";

const Installation = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    let imageLoaded = 0;
    const TOTAL_IMAGE = 6;
    const loaded = () => {
        imageLoaded++;
        if (imageLoaded >= TOTAL_IMAGE) {
            setIsLoaded(true);
        }
    };
    return (
        <>
            <LoadingScreen isLoaded={isLoaded} />
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    Installation
                </div>
                <div className="text-secondary-contrast text-2xl md:text-5xl mt-3 md:mt-4 ml-4 font-bold">
                    Executable Version
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Download JMC
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Download{" "}
                        <a href="https://github.com/WingedSeal/jmc/releases/latest/download/JMC.exe">
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
                        <Tab />
                        In "datapacks" folder of your world file (Usually{" "}
                        <code>.minecraft/saves/world_name/datapacks</code>).
                        Create a new datapack folder. And put JMC.exe in that
                        folder.
                    </p>
                </div>
                <img
                    src={require("../../assets/image/installation/file_location.png")}
                    alt="File Location Example"
                    width="927"
                    height="195"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Configuration
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Run JMC.exe and it'll greet you with configuration
                        settings. Select datapack's namespace, description and
                        pack_format. You can use default for{" "}
                        <code> Main JMC file</code> and{" "}
                        <code>Output directory</code>.
                    </p>
                </div>
                <img
                    src={require("../../assets/image/installation/config.png")}
                    alt="File Location Example"
                    width="1428"
                    height="255"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
                <div className="text-secondary-contrast text-2xl md:text-5xl mt-8 md:mt-12 ml-4 font-bold">
                    Python(pip) version
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Install python
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Download and install{" "}
                        <a
                            href="https://www.python.org/downloads/"
                            target="_blank"
                            rel="noreferrer"
                        >
                            python
                        </a>{" "}
                        version 3.10 or above.
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Open command prompt as administrator
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Search "cmd" in window search bar, right click at
                        Command Prompt and click{" "}
                        <code>Run as administrator</code>.
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Install the package
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Type <code>pip install jmcfunction --pre</code> and
                        press Enter (<code>--pre</code> will download latest
                        pre-release version)
                    </p>
                </div>
                <img
                    src={require("../../assets/image/installation/pip.png")}
                    alt="File Location Example"
                    width="990"
                    height="215"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    File location
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        In "datapacks" folder of your world file (Usually{" "}
                        <code>.minecraft/saves/world_name/datapacks</code>).
                        Type <code>cmd</code> in the path and press Enter to
                        open Command Prompt.
                    </p>
                </div>
                <img
                    src={require("../../assets/image/installation/file_location_python.png")}
                    alt="File Location Example"
                    width="761"
                    height="217"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
                <img
                    src={require("../../assets/image/installation/file_location_python_cmd.png")}
                    alt="File Location Example"
                    width="762"
                    height="165"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Configuration
                </div>
                <div className="text-white text-base md:text-2xl">
                    <p>
                        <Tab />
                        Type <code>jmc</code> in Command Prompt and it'll greet
                        you with configuration settings. Select datapack's
                        namespace, description and pack_format. You can use
                        default for <code> Main JMC file</code> and{" "}
                        <code>Output directory</code>.
                    </p>
                </div>
                <img
                    src={require("../../assets/image/installation/config_python.png")}
                    alt="File Location Example"
                    width="1234"
                    height="161"
                    className="max-w-[90vw] minecraft mx-auto my-3"
                    onLoad={() => {
                        loaded();
                    }}
                />
            </section>
        </>
    );
};
export default Installation;
