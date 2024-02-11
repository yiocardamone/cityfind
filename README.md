
## How to install
  
### 1. Install Python 3.11  
    brew install python  
    
### Install Poetry  & pyenv & virtualenv
    brew install poetry  
    brew install pyenv
    brew install pyenv-virtualenv
    
### 2. Append to shell startup file and restart terminal
#### Open shell startup file:

    source ~/.zshrc
    sudo nano ~/.zshrc
#### Append this:
``` 
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv init --path)"
``` 

### 3. Init python 3.11  
    pyenv install 3.11
    pyenv shell 3.11
	which python3
 	#Move to project directory and insert python location to bottom line:
	poetry env use ***

### 4. Install dependencies
	poetry install

### 5. Install docker && docker-compose
	brew install docker-compose

### 6. Run
	make run

