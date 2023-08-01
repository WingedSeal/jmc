import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const Import = () => {
    return (
        <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-secondary text-3xl md:text-6xl mx-auto">
                Import
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    <Tab />
                    All importing does is practically copying the code from
                    another file to main JMC file. The file name and folder
                    structure does not matter after the import. If the file is
                    already imported, importing it again will not do anything.
                </p>
                <p>
                    <Tab />
                    To import file from <code>
                        ./folder_name/file_name.jmc
                    </code>{" "}
                    to <code>./main.jmc</code>, use the following code in{" "}
                    <code>main.jmc</code>
                </p>
                <CodeBlock>
                    <CodeText type="operator">import</CodeText>{" "}
                    <CodeText type="string">"folder_name/file_name"</CodeText>;
                </CodeBlock>
                <p>
                    <Tab />
                    This is the folder structure for the import.
                </p>
                <CodeBlock>
                    ¦<Tab />
                    JMC.exe
                    <br />
                    ¦<Tab />
                    jmc_config.json
                    <br />
                    ¦<Tab />
                    main.jmc
                    <br />
                    ¦ <br />
                    +---folder_name
                    <br />
                    <Tab />
                    <Tab />
                    file_name.jmc
                </CodeBlock>
                <p>
                    <Tab />
                    You can also import every <code>.jmc</code> file in a folder
                    using wildcard import (asterisk)
                </p>
                <CodeBlock>
                    <CodeText type="operator">import</CodeText>{" "}
                    <CodeText type="string">"folder_name/*"</CodeText>;
                </CodeBlock>
            </div>
        </section>
    );
};
export default Import;
