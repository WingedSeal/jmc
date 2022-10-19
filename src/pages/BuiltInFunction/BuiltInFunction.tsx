import React from "react";
import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";

const BuiltInFunction = () => {
    return <section className="bg-[#2b0031] min-h-screen w-screen flex flex-col px-2 md:px-10 pt-[17vh]">
        <Feature id="player_on_event" summary="Player.onEvent()" keywords="scoreboard jump drop craft stats change" wip>
            <p>Run commands on positive change of scoreboard and reset the score.</p>
            <Command name="Player.onEvent" type="LoadOnly" params={[
                { key: "objective", type: "Objective" },
                { key: "function", type: "Function" },
            ]} />
        </Feature>
        <Feature id="player_on_event" summary="Player.onEvent()" keywords="scoreboard jump drop craft stats change" wip>
            <p>Run commands on positive change of scoreboard and reset the score.</p>
            <Command name="Player.onEvent" type="LoadOnly" params={[
                { key: "objective", type: "Objective" },
                { key: "function", type: "Function" },
            ]} />
        </Feature>
        <Feature id="player_on_event" summary="Player.onEvent()" keywords="scoreboard jump drop craft stats change" wip>
            <p>Run commands on positive change of scoreboard and reset the score.</p>
            <Command name="Player.onEvent" type="LoadOnly" params={[
                { key: "objective", type: "Objective" },
                { key: "function", type: "Function" },
            ]} />
        </Feature>
    </section>
};

export default BuiltInFunction;

