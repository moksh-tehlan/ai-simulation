# Movie Simulator with OpenAI Agents SDK

A dynamic movie simulation system where users provide a story seed, and AI agents create characters and storylines that autonomously interact while staying true to their personalities and the overall narrative arc.

## 🎯 Project Overview

This project implements a sophisticated movie simulation using the OpenAI Agents SDK, where:

- **User Input**: Provides a story seed (e.g., "A murder mystery in a small tech company")
- **Director Agent**: Creates timeline, characters, and initial setup
- **Character Agents**: Autonomous agents that interact and create plot developments
- **Story Evolution**: Dynamic narrative that adapts while maintaining coherence

## 📋 Phase 1: Foundation (Current)

**Status**: ✅ Complete

This phase establishes the core foundation:

- [x] Set up OpenAI Agents SDK environment
- [x] Create basic data models and context
- [x] Implement Director agent with basic setup tools
- [x] Test basic agent creation and handoffs

### Features Implemented

- **Data Models**: Complete story, character, and scene models
- **Director Agent**: Story orchestration and character creation
- **Simulation Framework**: Basic simulation runner with error handling
- **Testing**: Comprehensive test suite for all models
- **Documentation**: Full API documentation and examples

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (optional for basic functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie-simulator-agents-sdk
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Running the Simulator

**Basic Demo:**
```bash
python main.py
```

**Custom Story:**
```python
import asyncio
from movie_simulator import MovieSimulation

async def run_story():
    simulation = MovieSimulation()
    result = await simulation.run_simulation(
        "A romantic comedy about two rival coffee shop owners"
    )
    print(result)

asyncio.run(run_story())
```

## 🏗️ Architecture

### Core Components

```
movie_simulator/
├── core/
│   ├── agents/
│   │   ├── director.py          # Story orchestration agent
│   │   └── __init__.py
│   ├── models/
│   │   ├── story_models.py      # Data models
│   │   └── __init__.py
│   ├── simulation.py            # Main simulation runner
│   └── __init__.py
├── examples/
│   └── basic_story.py           # Example usage
├── tests/
│   └── test_models.py           # Test suite
└── __init__.py
```

### Data Models

**CharacterProfile**: Represents story characters with personality, motivations, and secrets
**StoryState**: Tracks story progression, genre, and dramatic tension
**SceneContext**: Manages scene-specific information and character presence
**MovieContext**: Central context holding all story state

### Agent Architecture

**Director Agent**: 
- Analyzes story seeds
- Creates compelling characters
- Establishes story timeline
- Monitors story progression

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

Test coverage includes:
- Data model validation
- Character creation and management
- Story state transitions
- Context management
- Error handling

## 📖 Usage Examples

### Basic Character Creation

```python
from movie_simulator.core.models.story_models import CharacterProfile, CharacterRole

character = CharacterProfile(
    id="detective_sarah",
    name="Detective Sarah Chen",
    background="Experienced homicide detective with intuitive skills",
    personality_traits=["analytical", "empathetic", "determined"],
    secrets=["Investigating her partner's suspicious death"],
    primary_motivation="Uncover the truth behind recent murders",
    secondary_goals=["Rebuild trust with the department"],
    fears=["Making mistakes that cost lives"],
    story_role=CharacterRole.PROTAGONIST
)
```

### Story Simulation

```python
import asyncio
from movie_simulator import MovieSimulation

async def create_murder_mystery():
    simulation = MovieSimulation()
    
    story_seed = """
    A murder mystery in a small tech startup during their IPO launch week.
    The victim is the CTO, found dead in the server room with a cryptic
    message written in code on the whiteboard.
    """
    
    result = await simulation.run_simulation(story_seed)
    
    # Access story context
    context = simulation.get_context()
    print(f"Generated {len(context.characters)} characters")
    print(f"Story genre: {context.story_state.genre.value}")
    
    return result

story = asyncio.run(create_murder_mystery())
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for full functionality
OPENAI_API_KEY=your_api_key_here

# Model selection
DIRECTOR_MODEL=gpt-4o           # For complex reasoning
SCENE_MANAGER_MODEL=gpt-4o-mini # For coordination
CHARACTER_MODEL=gpt-4o          # For personality consistency

# Simulation settings
MAX_INTERACTIONS=100
INTERVENTION_THRESHOLD=0.3
LOG_LEVEL=INFO

# Development
DEBUG=false
OPENAI_AGENTS_DISABLE_TRACING=false
```

### Model Configuration

The system supports multiple OpenAI models:

- **gpt-4o**: Best for complex reasoning (Director, Characters)
- **gpt-4o-mini**: Faster for coordination tasks (Scene Manager)
- **gpt-3.5-turbo**: Cost-effective alternative

## 🚦 Development Status

### Phase 1: Foundation ✅
- [x] Basic data models
- [x] Director agent implementation
- [x] Simulation framework
- [x] Testing infrastructure

### Phase 2: Core Tools (Next)
- [ ] Memory tools implementation
- [ ] Story progression tools
- [ ] Dramatic event injection
- [ ] Tool integration testing

### Phase 3: Character System
- [ ] Character agent factory
- [ ] Character-specific tools
- [ ] Personality consistency
- [ ] Character interactions

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

**Missing OpenAI API Key:**
- The system works in limited mode without an API key
- For full functionality, set `OPENAI_API_KEY` in your environment

**Module Not Found:**
- Ensure you're running from the project root directory
- Check that `movie_simulator` package is in your Python path

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
python main.py
```

## 📚 API Reference

### MovieSimulation

Main simulation class that orchestrates the movie creation process.

```python
class MovieSimulation:
    async def run_simulation(story_seed: str) -> str
    def get_context() -> Optional[MovieContext]
    def add_character(character: CharacterProfile) -> bool
```

### Data Models

See `movie_simulator/core/models/story_models.py` for complete API documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- Use type hints throughout
- Follow PEP 8 style guidelines
- Add docstrings to all public methods
- Write comprehensive tests
- Use meaningful variable names

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Agents SDK team for the powerful framework
- OpenAI for providing the language models
- The open-source community for inspiration and tools

---

**Next Phase**: Core Tools implementation with memory systems and story progression mechanics. 