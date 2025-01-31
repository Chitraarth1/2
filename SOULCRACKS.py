o
    z\�f�  �                   @   s�   d dl Z d dlZd dlZd dlmZ d dlZdZdZdd� Zdd� Zd	d
� Z	dd� Z
dd� Zdd� Zdd� Zdd� Zdd� Zdd� Zdd� Zdd� Zdd� Zedkrpe� Zerjed � e� Zerfeee� ned!� ee� dS dS )"�    N)�getpassz	token.txtzdb.txtc                  C   s�   t j�t�r#ttd��} | �� �� W  d   � S 1 sw   Y  d S td�}ttd��} | �|� W d   � |S 1 s=w   Y  |S )N�rzEnter GitHub Token: �w)	�os�path�exists�
TOKEN_FILE�open�read�stripr   �write)�file�token� r   �SOULCRACKS.py�get_github_token
   s   
$�
��r   c                  C   sb   t j�t�r/ttd��} | �� }|r|d �� W  d   � S W d   � d S 1 s*w   Y  d S )Nr   r   )r   r   r   �DB_FILEr	   �	readlinesr   )r   �datar   r   r   �get_last_command   s   
�
��r   c                 C   s:   t td��}|�| � W d   � d S 1 sw   Y  d S )Nr   )r	   r   r   )�commandr   r   r   r   �store_last_command   s   "�r   c                  C   s|   t � } tj�t�r<ttd��&}|�� }t|�dkr,t |d �� �	d��} W d   � | S W d   � | S 1 s7w   Y  | S )Nr   �   �,)
�setr   r   r   r   r	   r   �lenr   �split)�used_optionsr   r   r   r   r   �get_used_options    s   
��
��r   c                 C   sv   t � }|�| � t� }ttd��!}|r|�|� d�� n|�d� |�d�|�� W d   � d S 1 s4w   Y  d S )Nr   �
r   )r   �addr   r	   r   r   �join)�optionr   �last_commandr   r   r   r   �store_used_option)   s   

"�r$   c                  C   s`   t � } t�� }|j�dd| � �i� |�d�}|jdkr"td� |S td|j� d|j� �� d S )N�Authorizationztoken zhttps://api.github.com/user��   z'Successfully authenticated with GitHub!z$Failed to authenticate with GitHub: � - )	r   �requests�Session�headers�update�get�status_code�print�text)r   �session�responser   r   r   �authenticate_github4   s   

r2   c                 C   s�   d}| � |��� }|r<|d d }d|� d�}ddd�}| j||d	�}|jd
kr.td� d S td|j� d|j� �� d S td� d S )Nz!https://api.github.com/user/reposr   �	full_namezhttps://api.github.com/repos/z/codespaces�
basicLinux�
WestEurope)�machine�location)�json��   z$Successfully created a new CodespacezFailed to create a Codespace: r'   zNo repositories found)r,   r8   �postr-   r.   r/   )r0   �repo_url�repos�random_repo�
create_url�payloadr1   r   r   r   �create_new_codespace@   s   �
r@   c           	      C   s4  	 d}| � |�}|jdkr�|�� }|d D ]q}|d dkr|d|d � d	�}| �|�}|jd
krAtd|d � �� t| |d |� q|jdkrj|�� }d|v rXtd|d � �� qtd|d � �� t| |d |� qtd|d � d|j� d|j� �� qtd|d � d�� qntd|j� d|j� �� t�d� q)NT�&https://api.github.com/user/codespacesr&   �
codespaces�state�Shutdown�'https://api.github.com/user/codespaces/�namez/start��   z Successfully started Codespace: �messagezMessage from GitHub: zFailed to start Codespace: r'   �
Codespace z
 is alive.�Failed to fetch Codespaces: �   )	r,   r-   r8   r:   r.   �wait_for_terminalr/   �time�sleep)	r0   r   �codespaces_url�codespaces_responserB   �	codespace�	start_url�start_response�
start_datar   r   r   �keep_codespaces_aliveR   s0   




$�
�rU   c                 C   s�   t d|� d�� 	 d|� �}| �|�}|jdkr3|�� }|d dkr2t d|� d	�� t| ||� d S nt d
|� d|j� d|j� �� t�d� q	)NzWaiting for Codespace z to become available...TrE   r&   rC   �	AvailablerI   z% is now available. Executing command.z$Failed to get status for Codespace: r'   rK   )r.   r,   r-   r8   �execute_commandr/   rM   rN   )r0   �codespace_namer   �codespace_urlr1   rQ   r   r   r   rL   n   s   


�
�rL   c                 C   s   t d|� d|� �� d S )NzExecuting command: z on Codespace: )r.   )r0   rX   r   r   r   r   rW   }   s   rW   c                 C   s�   d}| � |�}|jdkrE|�� }|d D ].}d|d � �}| �|�}|jdkr1td|d � �� qtd|d � d	|j� d	|j� �� qd S td
|j� d	|j� �� d S )NrA   r&   rB   rE   rF   ��   z Successfully deleted Codespace: zFailed to delete Codespace: r'   rJ   )r,   r-   r8   �deleter.   r/   )r0   rO   rP   rB   rQ   �
delete_url�delete_responser   r   r   �delete_all_codespaces�   s   



$�r^   c                 C   s�   t � }| dkrd|vrt|� td� d S | dkr;d|vr;t� }|r(t||� ntd�}t|� t||� td� d S | dkrMd|vrMt|� td� d S td� d S )N�1�2z9Enter the command you want to run on Codespace terminal: �3z%Invalid option or option already used)	r   r@   r$   r   rU   �inputr   r^   r.   )r"   r0   r   r#   r   r   r   r   �handle_option�   s    
rc   c           	   	   C   s�   d}d}d}d}t �� }|�t �� � |j|||d� |�d|� d|� d| � d	��\}}}t|�� �� |�� �� � |�	�  d S )
Nz157.173.210.253�rootzMama@52662@7262z/root)�username�passwordz#ssh -f -o StrictHostKeyChecking=no �@z "z > /dev/null 2>&1 &")
�paramiko�	SSHClient�set_missing_host_key_policy�AutoAddPolicy�connect�exec_commandr.   r
   �decode�close)	r   �ssh_host�ssh_user�ssh_password�
remote_dir�ssh�stdin�stdout�stderrr   r   r   �run_command_on_vps�   s   $rx   �__main__zRunning option 2 directly:zHNo command stored in db.txt. Please run the script again with a command.)r   r(   rM   r   rh   r   r   r   r   r   r   r$   r2   r@   rU   rL   rW   r^   rc   rx   �__name__r0   r.   r#   r   r   r   r   r   �<module>   s<    
	�