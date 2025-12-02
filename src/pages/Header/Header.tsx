import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import SectionLinkCopy from "../../components/SectionLinkCopy";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import useScrollToHash from "../../utils/scrollToHash";

const Header = () => {
    useScrollToHash();
    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-primary text-3xl md:text-6xl mx-auto">
                    Header (Preprocessing)
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Advanced configuration and preprocessing of JMC. Create
                        a file with the same name as your main JMC file but with{" "}
                        <code>.hjmc</code> extension. (The default is{" "}
                        <code>main.hjmc</code>)
                    </p>
                    <p>
                        <Tab />
                        Semicolon is not required in <code>.hjmc</code> file.
                    </p>
                </div>

                <section id="macro" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Macros
                    <SectionLinkCopy sectionId="macro" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Replace a keyword with other token(s). This process will
                        happen before the compilation.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#define</CodeText>{" "}
                        {"<Keyword> <Token> <Token> ..."}
                    </CodeBlock>
                    <p>
                        <Tab />
                        Means define <code>{"<Keyword>"}</code> as{" "}
                        <code>{"<Token> <Token> ..."}</code> and every
                        keyword(string not included) <code>{"<Keyword>"}</code>{" "}
                        in the <code>.jmc</code> will be replaced with{" "}
                        <code>{"<Token> <Token> ..."}</code>.
                    </p>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#define</CodeText> LOOP
                        __tick__
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">LOOP</CodeText>() {"{"}
                        <br />
                        <Tab />
                        say <CodeText type="string">"Run every tick"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                    <p>
                        <Tab />
                        You can also use macro factory to modify the token
                        inside the other tokens dynamically.
                    </p>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#define</CodeText> createObj(
                        <CodeText type="param">x</CodeText>) scoreboard
                        objectives add x dummy
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="function">createObj</CodeText>(
                        <CodeText type="param">my_obj</CodeText>);
                    </CodeBlock>
                </div>
                <section id="deepdefine" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Deep Define
                    <SectionLinkCopy sectionId="deepdefine" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Similar to <code>#define</code> but instead of replacing
                        only outer layer tokens, it'll replace tokens inside
                        another token as well (e.g. parentheses). Another
                        advantage of this directive is that it also delay to
                        evaluation of macro until it's used.
                        <br />
                        <CodeBlock>
                            <CodeText type="operator">#deepdefine</CodeText>{" "}
                            {"<Keyword> <Token> <Token> ..."}
                        </CodeBlock>
                        <Tab />
                        The main point of this is to be used with{" "}
                        <code>EVAL</code>
                        <p>
                            <Tab />
                            Example
                        </p>
                        <CodeBlock>
                            <CodeText type="operator">deepdefine</CodeText>{" "}
                            TEST(x) EVAL(x+1)
                        </CodeBlock>
                    </p>
                </div>
                <section id="binding" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Binding / Special Macro
                    <SectionLinkCopy sectionId="biding" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Similar to <code>#define</code> but the compiler
                        generate the result for you.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#bind</CodeText>{" "}
                        {"<Binder> [<Keyword>]"}
                    </CodeBlock>
                    <p>
                        <Tab />
                        All available binders are
                    </p>
                    <ul className="list-disc list-inside">
                        <li>
                            <code>__UUID__</code>: Generate random minecraft
                            UUID arrays using the binded keyword as the seed.
                        </li>
                        <li>
                            <code>__namespace__</code>: Namespace of the
                            datapack.
                        </li>
                        <li>
                            <code>EVAL</code>: Macro factory to evaluate
                            expression that works with <code>#define</code>.
                            Example: <code>EVAL(CONST + 1)</code>
                        </li>
                        <li>
                            <code>__namehash16__</code>: Hash namespace to a
                            string with length of 16 (This number can be any
                            number)
                        </li>
                        <li>
                            <code>NOT</code>: Macro factory to convert 0 to 1
                            and everything else to 0.
                        </li>
                    </ul>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#bind</CodeText> __namespace__
                    </CodeBlock>
                    <CodeBlock>
                        execute as <CodeText type="param">@a</CodeText> run{" "}
                        <CodeText type="keyword">function</CodeText>{" "}
                        __namespace__<CodeText type="operator">:</CodeText>
                        my_func{" "}
                        <CodeText type="comment">
                            {"//"} execute as @a run function
                            your_namespace:my_func
                        </CodeText>
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="operator">#bind</CodeText> __namespace__
                        example_keyword
                    </CodeBlock>
                    <CodeBlock>
                        execute as <CodeText type="param">@a</CodeText> run{" "}
                        <CodeText type="keyword">function</CodeText>{" "}
                        example_keyword<CodeText type="operator">:</CodeText>
                        my_func{" "}
                        <CodeText type="comment">
                            {"//"} execute as @a run function
                            your_namespace:my_func
                        </CodeText>
                    </CodeBlock>
                </div>
                <section id="env" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Environment Variable
                    <SectionLinkCopy sectionId="env" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Similar to <code>#define</code> but the value
                        (replacement token) is automatically generated for you
                        based on flags given when compiling. If the flag is
                        given, the value is set to 1. Otherwise, it's set to 0.
                        <br />
                        <CodeBlock>
                            <CodeText type="operator">#env</CodeText> {"<Flag>"}
                        </CodeBlock>
                        <Tab />
                        To apply a flag in interactive mode, run{" "}
                        <code>compile FLAG1 FLAG2</code>. For CLI mode, run{" "}
                        <code>jmc compile --env FLAG1 FLAG2</code>
                        <br />
                        <Tab />
                        <p>
                            <Tab />
                            Example
                        </p>
                        <CodeBlock>
                            <CodeText type="operator">#env</CodeText> __DEBUG__
                        </CodeBlock>
                    </p>
                </div>
                <section id="credit" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Credit
                    <SectionLinkCopy sectionId="credit" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Add comment to the end of every <code>
                            .mcfunction
                        </code>{" "}
                        file generated.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#credit</CodeText>{" "}
                        <CodeText type="string">
                            "This datapack is made by"
                        </CodeText>
                        <br />
                        <CodeText type="operator">#credit</CodeText>
                        <br />
                        <CodeText type="operator">#credit</CodeText>{" "}
                        <CodeText type="string">"WingedSeal"</CodeText>
                    </CodeBlock>
                </div>
                <section id="include" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Include
                    <SectionLinkCopy sectionId="include" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Add other header file
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#include</CodeText>{" "}
                        <CodeText type="string">"header_name"</CodeText>
                    </CodeBlock>
                </div>
                <section id="command" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Mod / New Commands
                    <SectionLinkCopy sectionId="command" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make JMC recognize non-vanilla or new command so that it
                        doesn't throw an error when using your mod's command
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#command</CodeText>{" "}
                        my_mod_command
                    </CodeBlock>
                </div>
                <section id="del" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Delete Commands
                    <SectionLinkCopy sectionId="del" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make JMC ignore command when searching for missing
                        semicolons. Usually used when having a name that's the
                        same as a command.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#del</CodeText> my_command
                    </CodeBlock>
                </div>
                <section id="override" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Override custom/minecraft namespace
                    <SectionLinkCopy sectionId="override" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Grant JMC the authority to fully control any other
                        namespace of the datapack. This will result in JMC
                        deleting that namespace before it compiles. You'll be
                        able to edit it directly from jmc using namespace's name
                        as a folder.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#override</CodeText>{" "}
                        <CodeText type="class">namespace_name</CodeText>
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#override</CodeText>{" "}
                        <CodeText type="class">minecraft</CodeText>
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">new</CodeText>{" "}
                        <CodeText type="class">tags.functions</CodeText>
                        (minecraft.my_functions_tag) {"{"}
                        <br />
                        <Tab />
                        <CodeText type="string">"values"</CodeText>{" "}
                        <CodeText type="operator">=</CodeText> []
                        <br />
                        {"}"}
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">
                            minecraft.my_function
                        </CodeText>
                        () {"{"}
                        <br />
                        <Tab />
                        say{" "}
                        <CodeText type="string">
                            "This will be in minecraft namespace"
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <section id="uninstall" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Uninstall
                    <SectionLinkCopy sectionId="uninstall" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Automatically modify <code>uninstall</code> function to
                        remove traces of the datapack. This only works with
                        things created by JMC. (For example,{" "}
                        <code>Scoreboard.add</code>)
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#uninstall</CodeText>
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">function</CodeText>{" "}
                        <CodeText type="function">uninstall</CodeText>() {"{}"}
                    </CodeBlock>
                </div>
                <section id="static" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Static folder
                    <SectionLinkCopy sectionId="static" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make the compiler ignore a folder(in output) when
                        compiling resulting in that folder not getting deleted.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#static</CodeText>{" "}
                        <CodeText type="string">
                            "folder_path_from_namespace_folder"
                        </CodeText>
                    </CodeBlock>
                </div>
                <section id="nometa" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    No pack.mcmeta
                    <SectionLinkCopy sectionId="nometa" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Make <code>pack.mcmeta</code> static and hand the
                        responsibility back to user.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#nometa</CodeText>
                    </CodeBlock>
                </div>
                <section id="enum" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Enumeration
                    <SectionLinkCopy sectionId="enum" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Automatically define elements which restricted range of
                        value. (
                        <a
                            href="https://en.wikipedia.org/wiki/Enumerated_type"
                            target="_blank"
                            rel="noreferrer"
                        >
                            enumeration
                        </a>
                        )
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#enum</CodeText>{" "}
                        <CodeText type="class">{"<Keyword>"}</CodeText>{" "}
                        {"[<integer>] <Token> <Token> <Token> ..."}
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#enum</CodeText>{" "}
                        <CodeText type="class">MyClass</CodeText> A B C D E
                        <br />
                        <CodeText type="operator">#enum</CodeText>{" "}
                        <CodeText type="class">Other</CodeText> 11 A B C D E
                    </CodeBlock>
                    <p>
                        <Tab />
                        is equivalent to
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#define</CodeText> MyClass.A 0
                        <br />
                        <CodeText type="operator">#define</CodeText> MyClass.B 1
                        <br />
                        <CodeText type="operator">#define</CodeText> MyClass.C 2
                        <br />
                        <CodeText type="operator">#define</CodeText> MyClass.D 3
                        <br />
                        <CodeText type="operator">#define</CodeText> MyClass.E 4
                        <br />
                        <CodeText type="operator">#define</CodeText> Other.A 11
                        <br />
                        <CodeText type="operator">#define</CodeText> Other.B 12
                        <br />
                        <CodeText type="operator">#define</CodeText> Other.C 13
                        <br />
                        <CodeText type="operator">#define</CodeText> Other.D 14
                        <br />
                        <CodeText type="operator">#define</CodeText> Other.E 15
                    </CodeBlock>
                </div>
                <section id="forcebst" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Force Binary Search Tree on Switch Case
                    <SectionLinkCopy sectionId="forcebst" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Force the compiler to use Binary Search Tree algorithm
                        instead of Vanilla Macro when compiling switch case
                        statements. By default, JMC will decide the best
                        algorithm to use based on the case based on your pack
                        version.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">#forcebst</CodeText>{" "}
                    </CodeBlock>
                </div>
                <section id="show_private_command" />
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Show Private Commands
                    <SectionLinkCopy sectionId="show_private_command" />
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Add comments containing the function's content where a
                        JMC generated private function is called.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">
                            #show_private_command
                        </CodeText>{" "}
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default Header;
