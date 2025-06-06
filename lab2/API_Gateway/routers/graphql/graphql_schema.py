from ariadne import gql

schema_str = gql('''
    type User {
        userid: Int
        login: String
        role: String
        full_name: String
    }
    type Transaction {
        userid: Int!
        type: String
        count: Float
        timestamp: String
    }

    type AuthPayload {
        access_token: String!
        refresh_token: String!
    }

    type Query {
        getUser: User
        getAllUsers: [User]
        getTransactions(month: String!): [Transaction!]!
        refreshToken(refreshToken: String!): String!
        generateAndDownloadReport(month: String!, type: String!): String!
    } 
    type Mutation {
        registerUser(login: String!, password: String!, full_name: String!): User!
        loginUser(login: String!, password: String!): AuthPayload!
        addTransaction(type: String!, count: Float!, source: String!): Transaction!
    }
    type Subscription {
        transactionAdded: Transaction!
    }
''')