import React from "react";

const Header = () => {
    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-primary text-3xl md:text-6xl mx-auto">
                    Header (Preprocessing)
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Macros
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Lorem ipsum dolor sit amet consectetur adipisicing
                        elit. Neque dolorum, quae, tenetur libero aut dicta nisi
                        cumque nemo beatae debitis voluptatum inventore quaerat
                        harum expedita fugit, alias quasi velit consequuntur?
                    </p>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Credit
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Lorem ipsum dolor sit amet consectetur adipisicing
                        elit. Neque dolorum, quae, tenetur libero aut dicta nisi
                        cumque nemo beatae debitis voluptatum inventore quaerat
                        harum expedita fugit, alias quasi velit consequuntur?
                    </p>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    <s>Mod Commands</s>
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Lorem ipsum dolor sit amet consectetur adipisicing
                        elit. Neque dolorum, quae, tenetur libero aut dicta nisi
                        cumque nemo beatae debitis voluptatum inventore quaerat
                        harum expedita fugit, alias quasi velit consequuntur?
                    </p>
                </div>
            </section>
        </>
    );
};

export default Header;
