class ListboxHandler:
    @staticmethod
    def handle_drag_selection(listbox, indices, drop_index, files):
        if drop_index in indices:
            return files

        sorted_indices = sorted(list(indices))
        files_to_move = [files[i] for i in sorted_indices]
        
        # Remove files from end to not affect remaining indices
        for i in reversed(sorted_indices):
            del files[i]
        
        # Adjust drop index
        if drop_index > sorted_indices[-1]:
            drop_index -= len(sorted_indices)
        
        # Insert files at new position
        files[drop_index:drop_index] = files_to_move
        return files