















encoder = LabelEncoder()

## zmapowanie etykiet na wartości numeryczne z zakresu 1-13
LABEL_transform = encoder.fit_transform(LABEL_array)

## przygotowanie unikalnych wektorów one-hot dla każdej klasy
LABEL_onehot_array = tf.keras.utils.to_categorical(LABEL_transform)

train_labels, train_points, test_labels, test_points, valid_labels, valid_points = data_separate(
    LABEL_onehot_array, POINTS_array, class_label_counter
)

# konfiguracja struktury warstwowej modelu
model = Sequential([
    Dense(128, activation='relu', input_shape=(63,)),
    BatchNormalization(),
    Dropout(0.4),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
    Dense(len(encoder.classes_), activation='softmax')
])

## konfiguracja optymalizatora funkcji stratu
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

## przerwanie uczenie w przypadku braku efektynwej poprawy wartości funkcji straty
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
]

## wprowadzenie danych do modelu, rozpoczęcie procesu uczenia
run = model.fit(
    train_points, train_labels,
    validation_data=(valid_points, valid_labels),
    epochs=100,
    batch_size=64,
    callbacks=callbacks,
    verbose=1
)