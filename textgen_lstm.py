#!/usr/bin/env python3

import re, random
import numpy as np
import torch
import torch.nn.functional as F
from textgen import textgen
from torch import nn, optim

from rich.traceback import install
install()

# Model =======================================================================================
# https://towardsdatascience.com/text-generation-with-bi-lstm-in-pytorch-5fda6e7cc22c
# Embedding -> Bi-LSTM -> LSTM -> Linear

class Model(nn.ModuleList):

    def __init__(self, args):
        super(Model, self).__init__()

        self.batch_size = args["batch_size"]
        self.hidden_dim = args["hidden_dim"]
        self.input_size = args["vocab_size"]
        self.num_classes = args["vocab_size"]
        self.sequence_len = args["window"]

        # Dropout
        self.dropout = nn.Dropout(0.25)

        # Embedding layer
        self.embedding = nn.Embedding(self.input_size, self.hidden_dim, padding_idx=0)

        # Bi-LSTM
        # Forward and backward
        self.lstm_cell_forward = nn.LSTMCell(self.hidden_dim, self.hidden_dim)
        self.lstm_cell_backward = nn.LSTMCell(self.hidden_dim, self.hidden_dim)

        # LSTM layer
        self.lstm_cell = nn.LSTMCell(self.hidden_dim * 2, self.hidden_dim * 2)

        # Linear layer
        self.linear = nn.Linear(self.hidden_dim * 2, self.num_classes)


    def forward(self, x):
        # Bi-LSTM
        # hs = [batch_size x hidden_size]
        # cs = [batch_size x hidden_size]
        hs_forward = torch.zeros(x.size(0), self.hidden_dim)
        cs_forward = torch.zeros(x.size(0), self.hidden_dim)
        hs_backward = torch.zeros(x.size(0), self.hidden_dim)
        cs_backward = torch.zeros(x.size(0), self.hidden_dim)

        # LSTM
        # hs = [batch_size x (hidden_size * 2)]
        # cs = [batch_size x (hidden_size * 2)]
        hs_lstm = torch.zeros(x.size(0), self.hidden_dim * 2)
        cs_lstm = torch.zeros(x.size(0), self.hidden_dim * 2)

        # Weights initialization
        torch.nn.init.kaiming_normal_(hs_forward)
        torch.nn.init.kaiming_normal_(cs_forward)
        torch.nn.init.kaiming_normal_(hs_backward)
        torch.nn.init.kaiming_normal_(cs_backward)
        torch.nn.init.kaiming_normal_(hs_lstm)
        torch.nn.init.kaiming_normal_(cs_lstm)

        # From idx to embedding
        out = self.embedding(x)

        # Prepare the shape for LSTM Cells
        out = out.view(self.sequence_len, x.size(0), -1)

        forward = []
        backward = []

        # Unfolding Bi-LSTM
        # Forward
        for i in range(self.sequence_len):
            hs_forward, cs_forward = self.lstm_cell_forward(out[i], (hs_forward, cs_forward))
            forward.append(hs_forward)

        # Backward
        for i in reversed(range(self.sequence_len)):
            hs_backward, cs_backward = self.lstm_cell_backward(out[i], (hs_backward, cs_backward))
            backward.append(hs_backward)

        # LSTM
        for fwd, bwd in zip(forward, backward):
            input_tensor = torch.cat((fwd, bwd), 1)
            hs_lstm, cs_lstm = self.lstm_cell(input_tensor, (hs_lstm, cs_lstm))

        # Last hidden state is passed through a linear layer
        out = self.linear(hs_lstm)
        return out


# =============================================================================================

class LSTMTextGenerator(textgen):

    def __init__(self, windowsize):
        self.windowsize = windowsize # We slide a window over the character sequence and look at the next letter,
                                     # similar to the Markov chain order

    def init(self, filename):
        # Use this to generate one hot vector and filter characters
        self.letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " "]

        with open(f"./textfiles/{filename}.txt", "r") as file:
            lines = [line.lower() for line in file.readlines()] # lowercase list
            text = " ".join(lines) # single string
            self.charbase = [char for char in text if char in self.letters] # list of characters

    # Helper shit

    def __char_to_idx(self, char):
        return self.letters.index(char)

    def __idx_to_char(self, idx):
        return self.letters[idx]

    def __generate_char_sequences(self):
        # Example
        # [[21, 20, 15],
        #  [12, 12, 14]]
        prefixes = []

        # Example
        # [[1],
        #  [4]]
        suffixes = []

        print("Generating LSTM char sequences...")
        for i in range(len(self.charbase) - self.windowsize - 1):
            prefixes.append([self.__char_to_idx(char) for char in self.charbase[i:i+self.windowsize]])
            suffixes += [self.__char_to_idx(char) for char in self.charbase[i+self.windowsize+1]] # Bit stupid wrapping this in a list but removes possible type error

        # Enter numpy terretory NOW
        self.prefixes = np.array(prefixes)
        self.suffixes = np.array(suffixes)

        print(f"Prefixes shape: {self.prefixes.shape}")
        print(f"Suffixes shape: {self.suffixes.shape}")
        print("Completed.")

    # Interface shit

    def load(self):
        print(f"Loaded LSTM model with {len(self.charbase)} characters from file.")

        # TODO: Deduplicate args
        args = {
            "window": self.windowsize,
            "hidden_dim": 128,
            "vocab_size": len(self.letters),
            "batch_size": 128,
            "learning_rate": 0.001,
            "num_epochs": 50
        }

        self.model = Model(args)

        # model.load_state_dict(torch.load('weights/kommunistisches_manifest_lstm_model.pt'))

    def train(self):
        print(f"Training LSTM model with {len(self.charbase)} characters.")

        args = {
            "window": self.windowsize,
            "hidden_dim": 128,
            "vocab_size": len(self.letters),
            "batch_size": 128,
            "learning_rate": 0.001,
            "num_epochs": 50
        }

        self.__generate_char_sequences()

        # Model initialization
        self.model = Model(args)

        # Optimizer initialization
        optimizer = optim.RMSprop(self.model.parameters(), lr=args["learning_rate"])

        # Defining number of batches
        num_batches = int(len(self.prefixes) / args["batch_size"])

        # Set model in training mode
        self.model.train()

        # Training pahse
        for epoch in range(args["num_epochs"]):

            # Mini batches
            for i in range(num_batches):

                # Batch definition
                try:
                    x_batch = self.prefixes[i * args["batch_size"] : (i + 1) * args["batch_size"]]
                    y_batch = self.suffixes[i * args["batch_size"] : (i + 1) * args["batch_size"]]
                except:
                    x_batch = self.prefixes[i * args["batch_size"] :]
                    y_batch = self.suffixes[i * args["batch_size"] :]

                # Convert numpy array into torch tensors
                x = torch.from_numpy(x_batch).type(torch.long)
                y = torch.from_numpy(y_batch).type(torch.long)

                # Feed the model
                y_pred = self.model(x)

                # Loss calculation
                loss = F.cross_entropy(y_pred, y.squeeze())

                # Clean gradients
                optimizer.zero_grad()

                # Calculate gradientes
                loss.backward()

                # Updated parameters
                optimizer.step()

                print("Epoch: %d ,  loss: %.5f " % (epoch, loss.item()))

        torch.save(self.model.state_dict(), 'weights/kommunistisches_manifest_lstm_model.pt')


    def generate_sentence(self):
        # Set the model in evalulation mode
        self.model.eval()

        # Define the softmax function
        softmax = nn.Softmax(dim=1)

        # Randomly is selected the index from the set of sequences
        start = np.random.randint(0, len(self.prefixes)-1)

        # The pattern is defined given the random idx
        pattern = self.prefixes[start]

        # By making use of the dictionaries, it is printed the pattern
        print("\nPattern: \n")
        print(''.join([self.__idx_to_char(value) for value in pattern]), "\"")

        # In full_prediction we will save the complete prediction
        full_prediction = pattern.copy()

        # the prediction starts, it is going to be predicted a given
        # number of characters
        for _ in range(250):

            # the numpy patterns is transformed into a tesor-type and reshaped
            pattern = torch.from_numpy(pattern).type(torch.long)
            pattern = pattern.view(1,-1)

            # make a prediction given the pattern
            prediction = self.model(pattern)
            # it is applied the softmax function to the predicted tensor
            prediction = softmax(prediction)

            # the prediction tensor is transformed into a numpy array
            prediction = prediction.squeeze().detach().numpy()
            # it is taken the idx with the highest probability
            arg_max = np.argmax(prediction)

            # the current pattern tensor is transformed into numpy array
            pattern = pattern.squeeze().detach().numpy()
            # the window is sliced 1 character to the right
            pattern = pattern[1:]
            # the new pattern is composed by the "old" pattern + the predicted character
            pattern = np.append(pattern, arg_max)

            # the full prediction is saved
            full_prediction = np.append(full_prediction, arg_max)

        print("prediction: \n")
        print(''.join([self.__idx_to_char(value) for value in full_prediction]), "\"")

    def complete_sentence(self, prefix):
        pass
