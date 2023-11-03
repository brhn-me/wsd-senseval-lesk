import React, {useState} from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'
import {JSONTree} from 'react-json-tree';


const HighlightedSignatureSet = ({words, ambiguousWord}) => {
    return (
        <p>
            {words.map((word, index) => (
                <p className="highlighted-signature-set">
                    {word === ambiguousWord ? (
                        <span style={{color: 'green', fontWeight: 'bold'}}>{word}</span>
                    ) : (
                        <span>{word}</span>
                    )}
                    {index < words.length - 1 && ', '}
                </p>
            ))}
        </p>
    );
};


const SigHighlighter = ({sig, selectedWord, sentence}) => {
    return (
        <p>
            {
                sig && sig.map((word, index) => {
                    // Determine the className based on the word match
                    let className = '';
                    if (word === selectedWord) {
                        className = 'highlight-green';
                    } else if (sentence.includes(word)) {
                        className = 'highlight-red';
                    }

                    return (
                        <React.Fragment key={index}>
                            <span className={className}>{word}</span>
                            {index < sig.length - 1 ? ', ' : ''}
                        </React.Fragment>
                    );
                })
            }
        </p>
    );
};

function App() {
    const [sentence, setSentence] = useState('');
    const [selectedWord, setSelectedWord] = useState(null);
    const [definition, setDefinition] = useState(null);
    const [sense, setSense] = useState(null);
    const [wordInfo, setWordInfo] = useState(null);
    const [origSig, setOrgSig] = useState([]);
    const [relSig, setRelSig] = useState([]);

    const handleSearch = () => {
        setSelectedWord(null);
        setDefinition(null);
        setSense(null);
    };

    const handleWordClick = (word) => {
        setSelectedWord(word);
        setDefinition(null);
        setSense(null);
    };

    const findSense = async (lesk_type) => {
        const apiBase = `http://127.0.0.1:5000`
        const apiUrl = apiBase + `/${lesk_type}`;

        const postData = {
            context_sentence: sentence,
            ambiguous_word: selectedWord
        };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });
            const data = await response.json();

            // Assuming the API returns data in the format: {definition: "some definition", sense: "some sense"}
            setSense(data.sense);
            setDefinition(data.definition);

            if (lesk_type == 'extended_lesk') {
                setOrgSig(data.original_signature)
                setRelSig(data.related_signature)
            } else {
                setOrgSig([])
                setRelSig([]);
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        }

        try {
            const response = await fetch(apiBase + `/word_info/${selectedWord}`);
            const data = await response.json();
            setWordInfo(data);
            console.log(data)
        } catch (error) {
            console.error('Error fetching word info:', error);
        }
    };

    return (
        <React.Fragment>
            <div className="App d-flex justify-content-center">
                <div className="text-center mt-5 px-5"> {/* Added a top margin for a bit of spacing */}
                    <div className="search-container">
                        <h1 className="mb-4">Word Sense Disambiguation</h1>
                        <div className="input-group mb-3">
                            <input
                                type="text"
                                className="form-control sentence-input"
                                placeholder="Enter sentence..."
                                value={sentence}
                                onChange={e => setSentence(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                            />
                            <button className="btn btn-primary" onClick={handleSearch}>Search</button>
                        </div>
                    </div>


                    <div className="sentence-container">
                        {sentence && (
                            <div>
                                <p style={{maxWidth: 1000}}>
                                    {sentence.split(' ').map((word, idx) => (
                                        <span
                                            key={idx}
                                            style={{
                                                backgroundColor: word === selectedWord ? 'orange' : 'transparent',
                                                padding: '0 5px',
                                                cursor: "pointer"
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = 'yellow'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = word === selectedWord ? 'orange' : 'transparent'}
                                            onClick={() => handleWordClick(word)}
                                        >
              {word}
            </span>
                                    ))}
                                </p>
                            </div>
                        )}

                        {selectedWord && (
                            <div className="mb-3">
                                <button id="lesk" className="btn btn-outline-success m-1"
                                        onClick={() => findSense("basic_lesk")}>Find Sense
                                </button>
                                <button id="extended-lesk" className="btn btn-outline-success m-1"
                                        onClick={() => findSense("extended_lesk")}>Find Sense with Expanded Lesk
                                </button>
                            </div>
                        )}
                    </div>

                    {definition && sense && (
                        <React.Fragment>
                            <div className="mb-5">
                                <div className="sense-container mb-2">
                                    <h3 className="mb-3"><strong>Sense:</strong> {sense}</h3>
                                    <p className="definition"><strong>Definition:</strong> {definition}</p>
                                </div>
                                {
                                    origSig && origSig.length > 0 && (
                                        <div className="card mb-2">
                                            <div className="card-body">
                                                <h5 className="card-title">Original Signature</h5>
                                                <SigHighlighter sig={origSig} sentence={sentence}
                                                                selectedWord={selectedWord}/>
                                            </div>
                                        </div>

                                    )
                                }
                                {
                                    relSig && origSig.length > 0 && (
                                        <div className="card mb-2">
                                            <div className="card-body">
                                                <h5 className="card-title">Related Signature from Hypernym and Hyponyms</h5>
                                                <SigHighlighter sig={relSig} sentence={sentence}
                                                                selectedWord={selectedWord}/>
                                            </div>
                                        </div>
                                    )
                                }
                            </div>

                        </React.Fragment>

                    )}
                </div>
            </div>
            {wordInfo && (
                <div className="mb-2 mt-2 px-5">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title">Word Info</h5>
                            <div className="align-self-start w-100">
                                <JSONTree data={wordInfo}/>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </React.Fragment>


    )
        ;
}

export default App;
