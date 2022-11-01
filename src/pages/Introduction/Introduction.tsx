import React from "react";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const Introduction = () => {
    return (
        <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-secondary text-3xl md:text-6xl mx-auto">
                JMC Basics
            </div>
            <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                Preprocessing
            </div>
            <div className="text-white text-base md:text-2xl">
                <p>
                    <Tab />
                    Sometimes, coding datapack in mcfunction has very annoying
                    problems. To create a function, you need to create an
                    entirely new file. There's no way to format your code, and
                    no in-line comment. There are algorithms you need to
                    implement again and again. This is where a preprocessor can
                    help.
                </p>
                <p className="mt-6">
                    <Tab />
                    Once you start using JMC, it will take your preprocessed JMC
                    file and save it as normal mcfunction files and the rest of
                    the datapack.
                </p>
            </div>
        </section>
    );
};

export default Introduction;
