import Feature from "../../components/Feature";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const formattedText = (
    <Feature
        id="formatted_text"
        summary="Formatted Text"
        keywords="tutorial explaination help basic string color colour"
        className="text-tertiary"
    >
        <p>
            Some string paremeters(FormattedString) have special syntax you can
            use to format your string. JMC will parse it and turn it into{" "}
            <a
                href="https://minecraft.fandom.com/wiki/Raw_JSON_text_format"
                target="_blank"
                rel="noreferrer"
            >
                minecraft's raw json
            </a>
            .
        </p>

        <p>Formatted text comes in 2 form, </p>
        <ul>
            <li>
                <a
                    href="https://minecraft.fandom.com/wiki/Formatting_codes"
                    target="_blank"
                    rel="noreferrer"
                >
                    Minecraft's color codes
                </a>{" "}
                (Use <code>&</code> instead of <code>§</code>)
            </li>
            <li>JMC's Formatted Text</li>
        </ul>

        <p>The follow code is the syntax of JMC's Formatted Text,</p>
        <CodeBlock>
            <CodeText type="string">
                "{"text&<property, property>text&<property, property>text..."}"
            </CodeText>
        </CodeBlock>
        <p>Available properties are</p>
        <ul>
            <li>
                Color names
                <details className="ml-4">
                    <summary>List of colors</summary>
                    <ul>
                        <li>
                            <code>black</code>
                        </li>
                        <li>
                            <code>dark_blue</code>
                        </li>
                        <li>
                            <code>dark_green</code>
                        </li>
                        <li>
                            <code>dark_aqua</code>
                        </li>
                        <li>
                            <code>dark_red</code>
                        </li>
                        <li>
                            <code>dark_purple</code>
                        </li>
                        <li>
                            <code>gold</code>
                        </li>
                        <li>
                            <code>gray</code>
                        </li>
                        <li>
                            <code>dark_gray</code>
                        </li>
                        <li>
                            <code>blue</code>
                        </li>
                        <li>
                            <code>green</code>
                        </li>
                        <li>
                            <code>aqua</code>
                        </li>
                        <li>
                            <code>red</code>
                        </li>
                        <li>
                            <code>light_purple</code>
                        </li>
                        <li>
                            <code>yellow</code>
                        </li>
                        <li>
                            <code>white</code>
                        </li>
                        <li>
                            <code>reset</code>
                        </li>
                    </ul>
                </details>
            </li>
            <li>
                Color hex (For example: <code>#ffaa00</code>)
            </li>
            <li>
                <code>bold</code> or <code>!bold</code>
            </li>
            <li>
                <code>italic</code> or <code>!italic</code>
            </li>
            <li>
                <code>underlined</code> or <code>!underlined</code>
            </li>
            <li>
                <code>strikethrough</code> or <code>!strikethrough</code>
            </li>
            <li>
                <code>obfuscated</code> or <code>!obfuscated</code>
            </li>
            <li>
                JMC's variable (For example: <code>$my_var</code>)
            </li>
            <li>
                Scoreboard (For example: <code>my_objective:@s</code>)
            </li>
            <li>
                Selector (For example: <code>@a[tag=my_tag]</code>)
            </li>
        </ul>
        <p>
            Color will persist until new color is given. Text properties such as
            bold will persist until next set of properties. Scoreboard and
            Selector cannot be in the same set.
        </p>
        <p>
            To display <code>&</code> normally(escape), just type{" "}
            <code>&&</code>
        </p>
        <p>Examples:</p>
        <CodeBlock>
            <CodeText type="string">
                "{"&<gold,bold>"}Greetings, your score is {"&<$score,italic>"}
                {"&<bold>"}."
            </CodeText>
            <br />
            <CodeText type="string">
                "&6&lGreetings, your score is &o{"&<$score>"}&l."
            </CodeText>
        </CodeBlock>
        <p className="font-bold text-[#ffaa00] bg-black py-2">
            Greetings, your score is{" "}
            <span className="italic font-normal">10</span>.
        </p>
        <CodeBlock>
            <CodeText type="string">
                "{"&<green,@s>"} && {"&<@p[tag=god]>"} {"&<gold>"}are very
                cool."
            </CodeText>
            <br />
            <CodeText type="string">
                "&a{"&<@s>"} && {"&<@p[tag=god]>"} &6are very cool."
            </CodeText>
        </CodeBlock>
        <p className="text-[#55FF55] bg-black py-2">
            Zombie & WingedSeal{" "}
            <span className="text-[#ffaa00]">are very cool.</span>
        </p>
    </Feature>
);

export default formattedText;
